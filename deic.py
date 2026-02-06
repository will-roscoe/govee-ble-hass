from bleak import BleakClient, BleakScanner, discover
import asyncio 
async def run():
    scanner = BleakScanner()
    govee_ca0b = await scanner.find_device_by_address("D0:C9:07:13:CA:0B")
    govee_c539 = await scanner.find_device_by_address("D0:C9:07:16:C5:39")
    print(govee_ca0b.name)
    print(govee_c539.name)
    print(govee_ca0b.)
asyncio.run(run())
