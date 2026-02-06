'''Govee BLE for Home Assistant
by @will-roscoe'''

#imports
import asyncio
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.components.bluetooth import BluetoothScanningMode
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothProcessorCoordinator,
)
#from .const import DOMAIN
from homeassistant.const import Platform

PLATFORMS: list[Platform] = [Platform.SENSOR]

from your_library import DataParser

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Smart Light component."""
    # Add custom setup here if necessary
    raise NotImplementedError("Please implement async_setup")



_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up example BLE device from a config entry."""
    raise NotImplementedError("Please implement async_setup_entry, this is example code.")
    address = entry.unique_id
    data = DataParser()
    coordinator = hass.data.setdefault(DOMAIN, {})[
        entry.entry_id
    ] = PassiveBluetoothProcessorCoordinator(
        hass,
        _LOGGER,
        address=address,
        mode=BluetoothScanningMode.ACTIVE,
        update_method=data.update,
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(
        # only start after all platforms have had a chance to subscribe
        coordinator.async_start()
    )
    return True


    # Forward the setup to the light platform
    raise NotImplementedError("Please implement async_setup_entry")
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of an entry."""
 
    raise NotImplementedError("Please implement async_unload_entry")