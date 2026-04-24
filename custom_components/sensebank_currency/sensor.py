"""Sensor platform for Sense Bank USD/UAH rate."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timedelta

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    RestoreSensor,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

API_URL = "https://sensebank.ua/api/pages/currency-exchange"
TARGET_BLOCK_ORIGIN_ID = "ExchangeRateTabs"
TARGET_CURRENCY_LABEL = "USD/UAH"

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = 15

RATE_DESCRIPTION = SensorEntityDescription(
    key="usd_uah_buy",
    name="USD/UAH Buy Rate",
    device_class=SensorDeviceClass.MONETARY,
    native_unit_of_measurement="UAH",
    icon="mdi:currency-usd",
)

TREND_DESCRIPTION = SensorEntityDescription(
    key="usd_uah_trend",
    name="USD/UAH Trend",
    icon="mdi:trending-up",
)


async def _fetch_rate(session) -> dict | None:
    """Fetch USD/UAH buy rate from Sense Bank API."""
    async with session.get(API_URL) as resp:
        if resp.status != 200:
            raise UpdateFailed(f"API returned status {resp.status}")
        data = await resp.json(content_type=None)

    block = next(
        (b for b in data.get("blocks", []) if b.get("originId") == TARGET_BLOCK_ORIGIN_ID),
        None,
    )
    if block is None:
        raise UpdateFailed(f"Block '{TARGET_BLOCK_ORIGIN_ID}' not found in response")

    online_rates = block.get("attributes", {}).get("content", {}).get("online", [])
    rate = next(
        (r for r in online_rates if r.get("label") == TARGET_CURRENCY_LABEL), None
    )
    if rate is None:
        raise UpdateFailed(f"Currency '{TARGET_CURRENCY_LABEL}' not found in online rates")

    raw_value = rate.get("buy", {}).get("value")
    if raw_value is None:
        raise UpdateFailed(f"buy.value missing for '{TARGET_CURRENCY_LABEL}'")

    return {
        "rate": float(raw_value),
        "last_updated": datetime.now().isoformat(),
    }


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )

    session = async_get_clientsession(hass)

    async def async_update_data():
        return await _fetch_rate(session)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="sensebank_currency",
        update_method=async_update_data,
        update_interval=timedelta(minutes=scan_interval),
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        [
            SenseBankRateSensor(coordinator, RATE_DESCRIPTION),
            SenseBankTrendSensor(coordinator, TREND_DESCRIPTION),
        ]
    )


class SenseBankRateSensor(CoordinatorEntity, SensorEntity):
    """Current USD/UAH buy rate from Sense Bank."""

    _attr_has_entity_name = True

    def __init__(
            self,
            coordinator: DataUpdateCoordinator,
            description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"sensebank_{description.key}"

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("rate")

    @property
    def extra_state_attributes(self) -> dict:
        if self.coordinator.data is None:
            return {}
        return {"last_updated": self.coordinator.data.get("last_updated")}


class SenseBankTrendSensor(CoordinatorEntity, RestoreSensor):
    """Trend indicator for USD/UAH rate: going_high or going_low."""

    _attr_has_entity_name = True

    def __init__(
            self,
            coordinator: DataUpdateCoordinator,
            description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"sensebank_{description.key}"

        self._prev_rate: float | None = None
        self._current_trend: str = "going_high"

    async def async_added_to_hass(self) -> None:
        """Відновлюємо стан після перезавантаження Home Assistant."""
        await super().async_added_to_hass()

        # Дістаємо останній відомий стан з бази даних HA
        last_state = await self.async_get_last_state()

        if last_state is not None:
            # Відновлюємо тренд, якщо він був валідним
            if last_state.state in ("going_high", "going_low"):
                self._current_trend = last_state.state

            # Відновлюємо попередній курс з атрибутів
            if "previous_rate" in last_state.attributes:
                try:
                    self._prev_rate = float(last_state.attributes["previous_rate"])
                except (ValueError, TypeError):
                    pass

    @property
    def native_value(self) -> str:
        if self.coordinator.data is None:
            return self._current_trend

        current = self.coordinator.data.get("rate")
        if current is None:
            return self._current_trend

        if self._prev_rate is None:
            self._prev_rate = current
            return self._current_trend

        if current > self._prev_rate:
            self._current_trend = "going_high"
            self._prev_rate = current
        elif current < self._prev_rate:
            self._current_trend = "going_low"
            self._prev_rate = current

        return self._current_trend

    @property
    def icon(self) -> str:
        if self.native_value == "going_high":
            return "mdi:trending-up"
        return "mdi:trending-down"

    @property
    def extra_state_attributes(self) -> dict:
        return {"previous_rate": self._prev_rate}
