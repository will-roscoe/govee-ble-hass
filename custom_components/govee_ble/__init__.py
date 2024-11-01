"""The Smart Light integration."""
import asyncio
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Smart Light component."""
    # Add custom setup here if necessary
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Smart Light from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Forward the setup to the light platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "light")
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of an entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "light")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok