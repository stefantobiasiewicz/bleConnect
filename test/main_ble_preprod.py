import asyncio
import logging
import time

from bleak import BleakScanner, BleakClient

from ble.water_dispenser import CHARACTERISTIC_ON_OFF_UUID, SERWICE_WATER_DISPENSER_UUID


async def search_and_return_device():
    scanner = BleakScanner(service_uuids=[SERWICE_WATER_DISPENSER_UUID])
    devices = await scanner.discover()

    found_devices = []
    for device in devices:
        if SERWICE_WATER_DISPENSER_UUID in device.metadata.get('uuids'):
            print(f"Device found: {device.name} - {device.address}")
            found_devices.append(device)

    return found_devices

async def connect(device):
    if device is not None:
        client = BleakClient(device)
        await client.connect()
        return client

    return None


async def write_data(client, data):
    if client is not None:
        await client.write_gatt_char(char_specifier=CHARACTERISTIC_ON_OFF_UUID, data=data, response=True)

async def disconnect(client):
    if client is not None:
        await client.disconnect()


async def main():
    logging.basicConfig(level=logging.DEBUG)

    devices = await search_and_return_device()
    for device in devices:
        client = await connect(device)

        # await write_data(client, b'\x01')
        # time.sleep(5)
        # await write_data(client, b'\x00')
        await disconnect(client)


asyncio.run(main())
