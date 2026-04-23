"""Config flow for Sense Bank Currency integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.data_entry_flow import FlowResult

DOMAIN = "sensebank_currency"
DEFAULT_SCAN_INTERVAL = 15


class SenseBankCurrencyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sense Bank Currency."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title="Sense Bank USD/UAH",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=DEFAULT_SCAN_INTERVAL,
                    ): vol.All(int, vol.Range(min=1, max=1440)),
                }
            ),
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SenseBankCurrencyOptionsFlow:
        return SenseBankCurrencyOptionsFlow(config_entry)


class SenseBankCurrencyOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for scan interval."""

    async def async_step_init(
        self, user_input: dict | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL,
                            self.config_entry.data.get(
                                CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                            ),
                        ),
                    ): vol.All(int, vol.Range(min=1, max=1440)),
                }
            ),
        )
