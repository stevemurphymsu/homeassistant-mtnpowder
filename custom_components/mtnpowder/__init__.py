"""MtnPowder integration for Home Assistant."""

from __future__ import annotations

import asyncio
import contextlib
from datetime import datetime, timedelta
import json
import logging

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, FEED_URL

PLATFORMS = ["sensor", "weather"]

_LOGGER = logging.getLogger(__name__)


class MtnPowderCoordinator(DataUpdateCoordinator):
    """Coordinator for MtnPowder data updates."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry | None) -> None:
        """Initialize the coordinator."""
        self.session = aiohttp.ClientSession()
        self._last_etag = None
        self._last_modified = None
        self._last_data = None
        self._last_update_date = None
        self._updates_today = 0
        self._no_updates_today = 0
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
            update_method=self._async_fetch,  # type: ignore[arg-type]
            config_entry=config_entry,
        )

    async def _async_fetch(self):
        # Check date for daily reset
        current_date = datetime.now().date()
        if self._last_update_date != current_date:
            self._last_update_date = current_date
            self._updates_today = 0
            self._no_updates_today = 0
        # First, check with HEAD request if data has changed
        try:
            async with self.session.head(
                FEED_URL, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    _LOGGER.error("HEAD request failed: %s", resp.status)
                    self._no_updates_today += 1
                    return self._last_data
                etag = resp.headers.get("ETag")
                last_modified = resp.headers.get("Last-Modified")
                if (etag and etag == self._last_etag) or (
                    last_modified and last_modified == self._last_modified
                ):
                    _LOGGER.debug("Data not changed, using cached data")
                    self._no_updates_today += 1
                    return self._last_data
        except asyncio.CancelledError:
            raise
        except aiohttp.ClientError as err:
            _LOGGER.error("Error in HEAD request: %s", err)
            self._no_updates_today += 1
            return self._last_data

        # Data has changed or first fetch, do full GET
        self._updates_today += 1
        try:
            async with self.session.get(
                FEED_URL, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                text = await resp.text()
                # _LOGGER.debug("Response text: %s", text)
                # Update cached headers
                self._last_etag = resp.headers.get("ETag")
                _LOGGER.debug("ETAG: %s", self._last_etag)
                self._last_modified = resp.headers.get("Last-Modified")
                _LOGGER.debug("Last-Modified: %s", self._last_modified)
        except asyncio.CancelledError:
            raise
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching feed: %s", err)
            return self._last_data

        try:
            data = json.loads(text)
        except json.JSONDecodeError as err:
            _LOGGER.error("Error parsing JSON: %s", err)
            return self._last_data

        # Process data to create dict of mountain -> resort data
        # mountains = self.config_entry.data.get("mountains", [])

        stats = {
            "updates_today": self._updates_today,
            "no_updates_today": self._no_updates_today,
        }

        # for resort in data.get("Resorts", []):
        #   name = resort.get("Name")
        #   if name and name in mountains:
        #        resort_copy = resort.copy()
        #        resort_copy["stats"] = stats
        #        result[name] = resort_copy

        # Cache the result
        self._last_data = data
        return data


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the MtnPowder integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MtnPowder from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # create coordinator per config entry and store by entry_id
    coordinator = MtnPowderCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "title": entry.title,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        # cleanup coordinator for this entry
        entry_data = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        if entry_data:
            coord = entry_data.get("coordinator")
            with contextlib.suppress(Exception):
                await coord.session.close()
    return unload_ok
