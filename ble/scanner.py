from bleak import BleakScanner, BleakClient

from ble.water_dispenser import SERWICE_WATER_DISPENSER_UUID


async def search_and_return_device():
    scanner = BleakScanner()
    devices_local = await scanner.discover()

    found_devices = []
    for device in devices_local:
        if SERWICE_WATER_DISPENSER_UUID in device.metadata.get('uuids'):
            print(f"Device found: {device.name} - {device.address}")
            found_devices.append(device)

    return found_devices