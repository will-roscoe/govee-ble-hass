"""Config flow for Smart Light integration."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_MAC_ADDRESS, CONF_NAME
from homeassistant.core import callback
from .const import DOMAIN, DEFAULT_NAME, DEFAULT_BRIGHTNESS, DEFAULT_RGB_COLOR

_LOGGER = logging.getLogger(__name__)

@config_entries.HANDLERS.register(DOMAIN)
class SmartLightConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Light."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            # Validate MAC address and other data integrity checks
            mac_address = user_input[CONF_MAC_ADDRESS]
            if not self._is_valid_mac(mac_address):
                errors["base"] = "invalid_mac"
            else:
                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_MAC_ADDRESS): str,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Optional("initial_brightness", default=DEFAULT_BRIGHTNESS): vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
                vol.Optional("initial_color", default=DEFAULT_RGB_COLOR): vol.All(
                    vol.ExactSequence((vol.Coerce(int), vol.Coerce(int), vol.Coerce(int))),
                    vol.Length(min=3, max=3),
                ),
            }),
            errors=errors
        )

    def _is_valid_mac(self, mac):
        """Check if the given MAC address is valid."""
        # Placeholder for MAC address validation logic
        return True