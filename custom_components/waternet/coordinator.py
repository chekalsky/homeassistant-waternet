"""Daily tariff coordinator."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    TimestampDataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN
from .tariffs import TARIFF_URL, Tariffs, fetch_tariffs

_LOGGER = logging.getLogger(__name__)


class WaternetCoordinator(TimestampDataUpdateCoordinator[Tariffs]):
    """Fetch Waternet tariffs once a day."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(hours=24)
        )
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)},
            name="Waternet",
            manufacturer="Waternet",
            model="Drinkwater tarieven",
            configuration_url=TARIFF_URL,
        )

    async def _async_update_data(self) -> Tariffs:
        try:
            return await fetch_tariffs(async_get_clientsession(self.hass))
        except Exception as err:
            raise UpdateFailed(str(err) or type(err).__name__) from err
