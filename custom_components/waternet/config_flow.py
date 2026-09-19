"""Config flow for Waternet."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .tariffs import fetch_tariffs

_LOGGER = logging.getLogger(__name__)


class WaternetConfigFlow(ConfigFlow, domain=DOMAIN):
    """Add a single Waternet entry after a live fetch succeeds."""

    VERSION = 1

    async def async_step_user(
        self, _user_input: dict | None = None
    ) -> ConfigFlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        try:
            await fetch_tariffs(async_get_clientsession(self.hass))
        except Exception:
            _LOGGER.exception("Could not read Waternet tariffs")
            return self.async_abort(reason="cannot_connect")

        return self.async_create_entry(title="Waternet", data={})
