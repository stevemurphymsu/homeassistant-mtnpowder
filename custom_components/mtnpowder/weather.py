"""Weather platform for MtnPowder."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, time

from homeassistant.components.weather import WeatherEntity, WeatherEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPressure, UnitOfSpeed, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def _direction_to_bearing(direction: str) -> int | None:
    """Convert wind direction string to bearing in degrees."""
    directions = {
        "N": 0,
        "NNE": 22,
        "NE": 45,
        "ENE": 67,
        "E": 90,
        "ESE": 112,
        "SE": 135,
        "SSE": 157,
        "S": 180,
        "SSW": 202,
        "SW": 225,
        "WSW": 247,
        "W": 270,
        "WNW": 292,
        "NW": 315,
        "NNW": 337,
    }
    return directions.get(direction.upper())


def _map_condition(condition: str) -> str | None:
    """Map API condition to HA condition."""
    mapping = {
        "clear": "sunny",
        "cloudy": "cloudy",
        "fog": "fog",
        "hail": "hail",
        "lightning": "lightning",
        "rainy": "rainy",
        "snowy": "snowy",
        "windy": "windy",
        "partly cloudy": "partly-cloudy",
        # Add more if needed
    }
    return mapping.get(condition.lower(), "sunny")


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up the weather from a config entry."""

    entry_data = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if not entry_data:
        _LOGGER.error("MtnPowder entry data not found for %s", entry.entry_id)
        return

    coordinator = entry_data.get("coordinator")
    mountains = entry.data.get("mountains")

    if mountains:
        weather_entities = []
        for mountain in mountains:
            # Areas: Base, MidMountain, Summit
            resort = coordinator.data.get(mountain)
            areas = resort.get("CurrentConditions", [])
            for area in areas:
                weather_entities.append(MtnPowderWeather(coordinator, mountain, area))
        async_add_entities(weather_entities, True)


class MtnPowderWeather(CoordinatorEntity, WeatherEntity):
    """Weather entity for MtnPowder areas."""

    def __init__(
        self, coordinator: DataUpdateCoordinator, mountain: str, area: str
    ) -> None:
        """Initialize the weather entity."""
        super().__init__(coordinator)
        self._mountain = mountain
        self._area = area
        self._attr_name = f"{mountain} {area} Weather"
        self.unique_id = f"{mountain}_{area}_weather"
        self._attr_extra_state_attributes = {}

    @property
    def available(self):
        """Return if the entity is available."""
        return (
            self.coordinator.data is not None
            and self._mountain in self.coordinator.data
        )

    @property
    def native_temperature(self):
        """Return the temperature."""
        resort = self.coordinator.data.get(self._mountain)
        if resort:
            current_conditions = resort.get("CurrentConditions", {})
            area_data = current_conditions.get(self._area)
            if area_data:
                temp_c = area_data.get("TemperatureC")
                if temp_c and temp_c != "--":
                    try:
                        return float(temp_c)
                    except ValueError:
                        pass
        return None

    @property
    def native_temperature_unit(self):
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    @property
    def humidity(self):
        """Return the humidity."""
        resort = self.coordinator.data.get(self._mountain)
        if resort:
            current_conditions = resort.get("CurrentConditions", {})
            area_data = current_conditions.get(self._area)
            if area_data:
                humidity = area_data.get("Humidity")
                if humidity and humidity != "--":
                    try:
                        return int(humidity)
                    except ValueError:
                        pass
        return None

    @property
    def native_wind_speed(self):
        """Return the wind speed."""
        resort = self.coordinator.data.get(self._mountain)
        if resort:
            current_conditions = resort.get("CurrentConditions", {})
            area_data = current_conditions.get(self._area)
            if area_data:
                wind_kph = area_data.get("WindStrengthKph")
                if wind_kph and wind_kph != "--":
                    try:
                        return float(wind_kph)
                    except ValueError:
                        pass
        return None

    @property
    def native_wind_speed_unit(self):
        """Return the wind speed unit."""
        return UnitOfSpeed.KILOMETERS_PER_HOUR

    @property
    def wind_bearing(self):
        """Return the wind bearing."""
        resort = self.coordinator.data.get(self._mountain)
        if resort:
            current_conditions = resort.get("CurrentConditions", {})
            area_data = current_conditions.get(self._area)
            if area_data:
                direction = area_data.get("WindDirection")
                if direction:
                    return _direction_to_bearing(direction)
        return None

    @property
    def native_pressure(self):
        """Return the pressure."""
        resort = self.coordinator.data.get(self._mountain)
        if resort:
            current_conditions = resort.get("CurrentConditions", {})
            area_data = current_conditions.get(self._area)
            if area_data:
                pressure_mb = area_data.get("PressureMB")
                if pressure_mb and pressure_mb != "--":
                    try:
                        return float(pressure_mb)
                    except ValueError:
                        pass
        return None

    @property
    def native_pressure_unit(self):
        """Return the pressure unit."""
        return UnitOfPressure.MBAR

    @property
    def condition(self):
        """Return the weather condition."""
        resort = self.coordinator.data.get(self._mountain)
        if resort:
            current_conditions = resort.get("CurrentConditions", {})
            area_data = current_conditions.get(self._area)
            if area_data:
                api_condition = area_data.get("Skies")
                if api_condition:
                    return _map_condition(api_condition)
        return None

    @property
    def forecast(self):
        """Return the forecast."""
        resort = self.coordinator.data.get(self._mountain)
        if not resort:
            return None
        forecast_data = resort.get("Forecast", {})
        current_conditions = resort.get("CurrentConditions", {})
        area_data = current_conditions.get(self._area)
        if not forecast_data:
            return None
        # Get area's temp high/low in F
        temp_high_f_area = area_data.get("TemperatureHighF")
        temp_low_f_area = area_data.get("TemperatureLowF")
        forecasts = []
        day_keys = ["OneDay", "TwoDay", "ThreeDay", "FourDay", "FiveDay"]
        for day_key in day_keys:
            day_data = forecast_data.get(day_key)
            if not day_data:
                continue
            date_str = day_data.get("date")
            if not date_str:
                continue
            try:
                date = datetime.fromisoformat(date_str)
            except ValueError:
                continue
            condition = _map_condition(day_data.get("conditions", ""))
            temp_high = day_data.get("temp_high_f")
            temp_low = day_data.get("temp_low_f")
            if temp_high == "--" or temp_low == "--":
                continue
            try:
                if day_key == "OneDay" and temp_high_f_area is not None:
                    temp_high_f = temp_high_f_area
                    temp_low_f = temp_low_f_area
                else:
                    temp_high_f = float(temp_high)
                    temp_low_f = float(temp_low)
            except ValueError:
                continue
            # Daytime forecast
            snow_day = day_data.get("forecasted_snow_day_in", "0")
            if "-" in snow_day:
                snow_day = snow_day.split("-")[0]
            try:
                precip_day = float(snow_day) * 25.4 if snow_day != "0" else 0.0
            except ValueError:
                precip_day = 0.0
            daytime_forecast = {
                "datetime": date.replace(hour=12, minute=0, second=0, microsecond=0),
                "condition": condition,
                "temperature": temp_high_f,
                "templow": temp_low_f,
                "precipitation": precip_day,
            }
            forecasts.append(daytime_forecast)
            # Nighttime forecast
            snow_night = day_data.get("forecasted_snow_night_in", "0")
            if "-" in snow_night:
                snow_night = snow_night.split("-")[0]
            try:
                precip_night = float(snow_night) * 25.4 if snow_night != "0" else 0.0
            except ValueError:
                precip_night = 0.0
            nighttime_forecast = {
                "datetime": (date + timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ),
                "condition": condition,
                "temperature": temp_low_f,
                "templow": temp_low_f,
                "precipitation": precip_night,
            }
            forecasts.append(nighttime_forecast)
        return forecasts

    async def async_added_to_hass(self):
        """Handle entity being added to hass."""
        await super().async_added_to_hass()
        if not self.coordinator.data:
            return
        self._handle_coordinator_update()

    def _handle_coordinator_update(self) -> None:
        """Handle coordinator update."""
        resort = self.coordinator.data.get(self._mountain)
        if resort:
            current_conditions = resort.get("CurrentConditions", {})
            area_data = current_conditions.get(self._area)
            if area_data:
                self._attr_extra_state_attributes = {
                    k: v
                    for k, v in area_data.items()
                    if k
                    not in (
                        "Name",
                        "Icon",
                        "IconFADefault",
                        "TemperatureF",
                        "TemperatureC",
                        "TemperatureLowF",
                        "TemperatureHighF",
                        "TemperatureLowC",
                        "TemperatureHighC",
                        "PressureIN",
                        "PressureMB",
                        "WindDirection",
                        "WindStrengthMph",
                        "WindStrengthKph",
                        "HumidityC",
                        "HumidityF",
                        "DewPointC",
                        "DewPointF",
                        "Conditions",
                    )
                }
            else:
                self._attr_extra_state_attributes = {}
        else:
            self._attr_extra_state_attributes = {}
        self.async_write_ha_state()
