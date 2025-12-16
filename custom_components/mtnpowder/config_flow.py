"""Config flow for MtnPowder integration."""

from __future__ import annotations

import contextlib

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv

from . import MtnPowderCoordinator
from .const import DEFAULT_NAME, DOMAIN


class MtnPowderFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for MtnPowder."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step where we let the user choose a mountain."""
        if user_input is None:
            # Temporarily fetch the feed to derive a list of mountain choices.
            coordinator = MtnPowderCoordinator(self.hass, None)
            try:
                await coordinator.async_refresh()
                feed = coordinator.data
            finally:
                # close the temporary session if present
                with contextlib.suppress(Exception):
                    await coordinator.session.close()

            choices = []
            if feed and isinstance(feed, dict) and "Resorts" in feed:
                for resort in feed["Resorts"]:
                    name = resort.get("Name")
                    if name and name not in choices:
                        choices.append(name)

            if not choices:
                choices = ["All"]

            schema = vol.Schema(
                {
                    vol.Required("mountains"): cv.multi_select(choices),
                }
            )
            return self.async_show_form(step_id="user", data_schema=schema)

        mountains = user_input.get("mountains", "None")

        return self.async_create_entry(title=mountains, data={"mountains": mountains})
