import asyncio
import logging
import time

from bleak import BleakScanner, BleakClient

from devices import SERWICE_WATER_DISPENSER_UUID, CHARACTERISTIC_ON_OFF_UUID


async def main():
    scanner = BleakScanner(service_uuids=[SERWICE_WATER_DISPENSER_UUID])
    devices = await scanner.discover()

    for device in devices:
        if SERWICE_WATER_DISPENSER_UUID in device.metadata.get('uuids'):
            print(f"Device found: {device.name} - {device.address}")
            client = BleakClient(device)
            await client.connect()
            services = client.services
            for service in services:
                print(f"Service found: {service}")
                characteristics = service.characteristics
                for characteristic in characteristics:
                    print(f"Characteristic: {characteristic}")

            await client.write_gatt_char(char_specifier=CHARACTERISTIC_ON_OFF_UUID, data=b'\x01', response=True)
            time.sleep(5)
            await client.write_gatt_char(char_specifier=CHARACTERISTIC_ON_OFF_UUID, data=b'\x00', response=True)

            await client.disconnect()



logging.basicConfig(level=logging.DEBUG)
asyncio.run(main())
