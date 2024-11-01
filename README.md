# govee-ble-hass
 A component to connect and control govee lights over BLE, for products that don't have LAN control.
----
[![HACS](https://github.com/will-roscoe/govee-ble-hass/actions/workflows/validate.yaml/badge.svg)](https://github.com/will-roscoe/govee-ble-hass/actions/workflows/validate.yaml)


I got fustrated with the lack of Local API on some of Govee's devices and by the extremely limited amount of calls they allow to their own API (as well as the exceptionally high latency) so i have been working on a custom integration for Home Assistant to talk to Govee Lights through BLE since they have seemingly always had bluetooth communication on all of their devices. This repo is very much in a work in progress but i have implemented the main functions (toggling on/off, brightness, rgb). Any contributions to this project would be extremely helpful.

>[!Note]
> there is no official documentation/API for communicating with Govee's Lights over BLE, and as such most of the payloads have been found by reverse enginering. Have a look at [Govee-Reverse-Engineering](https://github.com/egold555/Govee-Reverse-Engineering) for in depth work by the contributors over there  
