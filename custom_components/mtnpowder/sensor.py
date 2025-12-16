"""Sensor platform for MtnPowder feed."""

from __future__ import annotations

import logging
import re

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant, config, async_add_entities, discovery_info=None
):
    """Deprecated setup - not used when using config entries."""
    return


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up the sensor from a config entry."""

    entry_data = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if not entry_data:
        _LOGGER.error("MtnPowder entry data not found for %s", entry.entry_id)
        return

    coordinator = entry_data.get("coordinator")
    mountains = entry.data.get("mountains")

    if mountains:
        for mountain in mountains:
            sensors = [MtnPowderSensor(coordinator, mountain, ("operating_status",))]
            # SnowReport keys that are simple values (not dict or list)
            snow_keys = [
                "BaseConditions",
                "Report",
                "AdditionalText",
                "News",
                "Alert",
                "StormRadar",
                "StormRadarButtonText",
                "SafetyReport",
                "SafetyReportFrench",
                "LiftNotification",
                "OpenTerrainAcres",
                "TotalTerrainAcres",
                "StormTotalIn",
                "StormTotalCM",
                "AnnualAverageSnowfallIn",
                "AnnualAverageSnowfallCm",
                "SnowBaseRangeIn",
                "SnowBaseRangeCM",
                "SeasonTotalIn",
                "SeasonTotalCm",
                "SecondarySeasonTotalIn",
                "SecondarySeasonTotalCm",
                "OpenTerrainHectares",
                "TotalTerrainHectares",
                "TotalOpenTrails",
                "TotalTrails",
                "TotalTrailsMakingSnow",
                "GroomedTrails",
                "TotalOpenLifts",
                "TotalLifts",
                "TotalOpenActivities",
                "TotalActivities",
                "TotalOpenParks",
                "TotalParks",
                "OpenNightParks",
                "TotalNightParks",
                "TotalParkFeatures",
                "OpenNightTrails",
                "TotalNightTrails",
                "GroomingActive",
                "SnowMakingActive",
                "TotalHalfpipes",
                "OpenHalfpipes",
            ]
            for key in snow_keys:
                sensors.append(
                    MtnPowderSensor(coordinator, mountain, ("snow_report", key))
                )

            # MountainAreas sensors
            resort_data = coordinator.data.get(mountain, {})
            mountain_areas = resort_data.get("MountainAreas", [])
            for area in mountain_areas:
                sensors.append(
                    MtnPowderSensor(coordinator, mountain, ("area", area["Name"]))
                )

            # Trails sensors
            for area in mountain_areas:
                for trail in area.get("Trails", []):
                    sensors.append(
                        MtnPowderSensor(
                            coordinator,
                            mountain,
                            ("trail", area["Name"], trail["Name"]),
                        )
                    )

            # Lifts sensors
            for area in mountain_areas:
                for lift in area.get("Lifts", []):
                    sensors.append(
                        MtnPowderSensor(
                            coordinator,
                            mountain,
                            ("lift", area["Name"], lift["Name"]),
                        )
                    )

            # Activities sensors
            for area in mountain_areas:
                for activity in area.get("Activities", []):
                    sensors.append(
                        MtnPowderSensor(
                            coordinator,
                            mountain,
                            ("activity", area["Name"], activity["Name"]),
                        )
                    )

            async_add_entities(sensors, True)

            # Add update tracking sensors
            async_add_entities(
                [
                    MtnPowderSensor(coordinator, mountain, ("stats", "updates_today")),
                    MtnPowderSensor(
                        coordinator, mountain, ("stats", "no_updates_today")
                    ),
                ],
                True,
            )


class MtnPowderSensor(CoordinatorEntity, SensorEntity, RestoreEntity):
    """Sensor representing MtnPowder data."""

    def __init__(
        self, coordinator: DataUpdateCoordinator, mountain: str, sensor_type: tuple
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._mountain = mountain
        self._sensor_type = sensor_type
        if sensor_type[0] == "operating_status":
            self._attr_name = f"{mountain} Operating Status"
            self._attr_unique_id = f"{mountain}_operating_status"
        elif sensor_type[0] == "snow_report":
            key = sensor_type[1]
            # Add spaces between words
            display_key = re.sub(r"([a-z])([A-Z])", r"\1 \2", display_key)
            self._attr_name = f"{mountain} {display_key}"
            self._attr_unique_id = f"{mountain}_snow_report_{key}"
            # Add unit_of_measurement for known units
            if key.endswith("In"):
                self._attr_unit_of_measurement = "in"
            elif key.endswith("CM"):
                self._attr_unit_of_measurement = "cm"
            elif "Acres" in key:
                self._attr_unit_of_measurement = "acre"
            elif "Hectares" in key:
                self._attr_unit_of_measurement = "ha"
            # For counts, no unit needed
        elif sensor_type[0] == "area":
            area_name = sensor_type[1]
            self._attr_name = f"{mountain} {area_name} Open Trails"
            self._attr_unique_id = (
                f"{mountain}_area_{area_name.replace(' ', '_').lower()}"
            )
        elif sensor_type[0] == "trail":
            area_name = sensor_type[1]
            trail_name = sensor_type[2]
            self._attr_name = f"{mountain} {area_name} {trail_name}"
            self._attr_unique_id = f"{mountain}_trail_{area_name.replace(' ', '_').lower()}_{trail_name.replace(' ', '_').lower()}"
        elif sensor_type[0] == "lift":
            area_name = sensor_type[1]
            lift_name = sensor_type[2]
            self._attr_name = f"{mountain} {area_name} {lift_name} Lift"
            self._attr_unique_id = f"{mountain}_lift_{area_name.replace(' ', '_').lower()}_{lift_name.replace(' ', '_').lower()}"
        elif sensor_type[0] == "activity":
            area_name = sensor_type[1]
            activity_name = sensor_type[2]
            self._attr_name = f"{mountain} {area_name} {activity_name}"
            self._attr_unique_id = f"{mountain}_activity_{area_name.replace(' ', '_').lower()}_{activity_name.replace(' ', '_').lower()}"
        elif sensor_type[0] == "stats":
            stat_type = sensor_type[1]
            display_name = stat_type.replace("_", " ").title()
            self._attr_name = f"{mountain} {display_name}"
            self._attr_unique_id = f"{mountain}_{stat_type}"
        self._state = None
        self._attr_extra_state_attributes = {}

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self._state

    @property
    def available(self):
        """Return if the sensor is available."""
        return (
            self.coordinator.data is not None
            and self._mountain in self.coordinator.data
        )

    async def async_added_to_hass(self):
        """Handle entity being added to hass."""
        await super().async_added_to_hass()
        if not self.coordinator.data:
            return
        self._handle_coordinator_update()

    def _handle_coordinator_update(self) -> None:
        resort = self.coordinator.data.get(self._mountain)
        if not resort:
            self._state = None
        else:
            if self._sensor_type[0] == "operating_status":
                self._state = resort.get("OperatingStatus")
            elif self._sensor_type[0] == "snow_report":
                key = self._sensor_type[1]
                snow_report = resort.get("SnowReport", {})
                value = snow_report.get(key)
                if isinstance(value, str) and len(value) > 255:
                    self._state = value[:252] + "..."
                else:
                    self._state = value
            elif self._sensor_type[0] == "area":
                area_name = self._sensor_type[1]
                mountain_areas = resort.get("MountainAreas", [])
                area = next((a for a in mountain_areas if a["Name"] == area_name), None)
                if area:
                    self._state = area.get("OpenTrailsCount", 0)
                    self._attr_extra_state_attributes = {
                        "total_trails_count": area.get("TotalTrailsCount"),
                        "last_update": area.get("LastUpdate"),
                    }
                else:
                    self._state = None
                    self._attr_extra_state_attributes = {}
            elif self._sensor_type[0] == "trail":
                area_name = self._sensor_type[1]
                trail_name = self._sensor_type[2]
                mountain_areas = resort.get("MountainAreas", [])
                area = next((a for a in mountain_areas if a["Name"] == area_name), None)
                if area:
                    trails = area.get("Trails", [])
                    trail = next((t for t in trails if t["Name"] == trail_name), None)
                    if trail:
                        value = trail.get("StatusEnglish", "unknown")
                        if isinstance(value, str) and len(value) > 255:
                            self._state = value[:252] + "..."
                        else:
                            self._state = value
                        self._attr_extra_state_attributes = {
                            "difficulty": trail.get("Difficulty"),
                            "snow_making": trail.get("SnowMaking"),
                            "grooming": trail.get("Grooming"),
                            "night_skiing": trail.get("NightSkiing"),
                            "moguls": trail.get("Moguls"),
                            "glades": trail.get("Glades"),
                            "touring": trail.get("Touring"),
                            "nordic": trail.get("Nordic"),
                            "terrain_park_on_run": trail.get("TerrainParkOnRun"),
                            "run_of_the_day": trail.get("RunOfTheDay"),
                            "trail_summary": trail.get("TrailSummary"),
                            "terrain_park_features": trail.get("TerrainParkFeatures"),
                            "update_date": trail.get("UpdateDate"),
                        }
                    else:
                        self._state = None
                        self._attr_extra_state_attributes = {}
                else:
                    self._state = None
                    self._attr_extra_state_attributes = {}
            elif self._sensor_type[0] == "lift":
                area_name = self._sensor_type[1]
                lift_name = self._sensor_type[2]
                mountain_areas = resort.get("MountainAreas", [])
                area = next((a for a in mountain_areas if a["Name"] == area_name), None)
                if area:
                    lifts = area.get("Lifts", [])
                    lift = next((l for l in lifts if l["Name"] == lift_name), None)
                    if lift:
                        value = lift.get("StatusEnglish", "unknown")
                        if isinstance(value, str) and len(value) > 255:
                            self._state = value[:252] + "..."
                        else:
                            self._state = value
                        self._attr_extra_state_attributes = {
                            k: v
                            for k, v in lift.items()
                            if k not in ("Status", "StatusEnglish", "Id")
                        }
                    else:
                        self._state = None
                        self._attr_extra_state_attributes = {}
                else:
                    self._state = None
                    self._attr_extra_state_attributes = {}
            elif self._sensor_type[0] == "activity":
                area_name = self._sensor_type[1]
                activity_name = self._sensor_type[2]
                mountain_areas = resort.get("MountainAreas", [])
                area = next((a for a in mountain_areas if a["Name"] == area_name), None)
                if area:
                    activities = area.get("Activities", [])
                    activity = next(
                        (act for act in activities if act["Name"] == activity_name),
                        None,
                    )
                    if activity:
                        value = activity.get("StatusEnglish", "unknown")
                        if isinstance(value, str) and len(value) > 255:
                            self._state = value[:252] + "..."
                        else:
                            self._state = value
                        self._attr_extra_state_attributes = {
                            k: v
                            for k, v in activity.items()
                            if k not in ("Status", "StatusEnglish", "Id")
                        }
                    else:
                        self._state = None
                        self._attr_extra_state_attributes = {}
                else:
                    self._state = None
                    self._attr_extra_state_attributes = {}
            elif self._sensor_type[0] == "stats":
                stat_type = self._sensor_type[1]
                stats = resort.get("stats", {})
                self._state = stats.get(stat_type, 0)
                self._attr_extra_state_attributes = {}
            else:
                self._state = None
                self._attr_extra_state_attributes = {}
        self.async_write_ha_state()
