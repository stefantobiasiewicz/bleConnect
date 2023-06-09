import asyncio
from asyncio import AbstractEventLoop

from bleak import BleakClient

SERWICE_WATER_DISPENSER_UUID = "12345678-1234-5678-1234-56789abcdef1"

CHARACTERISTIC_IMPULS_SET_UUID = "12345678-1234-5678-1234-56789abcdef2"
CHARACTERISTIC_RUN_UUID = "12345678-1234-5678-1234-56789abcdef3"
CHARACTERISTIC_IDENTIFY_UUID = "12345678-1234-5678-1234-56789abcdef4"
CHARACTERISTIC_ON_OFF_UUID = "12345678-1234-5678-1234-56789abcdef5"

class BleDevice:
    def __init__(self, client: BleakClient, loop: AbstractEventLoop):
        self.client = client
        self.loop = loop

    @property
    def is_connected(self):
        return self.client.is_connected

    def connect(self):
        if not self.is_connected:
            future = asyncio.run_coroutine_threadsafe(self.client.connect(), self.loop)
            future.result()

    def connect_async(self):
        if not self.is_connected:
            future = asyncio.run_coroutine_threadsafe(self.client.connect(), self.loop)

    def disconnect(self):
        asyncio.run_coroutine_threadsafe(self.client.disconnect(), self.loop)

    def write_gatt_char(self, char_specifier, data, response=False):
        asyncio.run_coroutine_threadsafe(self.client.write_gatt_char(char_specifier, data, response), self.loop)

    def check_if_ready(self):
        raise Exception("not implemented")
        pass

import logging

# Utwórz obiekt loggera
logger = logging.getLogger(__name__)

class WaterDispenser(BleDevice):
    async def wd_set_impuls(self, impuls: int):
        self.check_if_ready()

        try:
            if self.client is not None:
                logger.info(f"wd_set_impuls - Input: impuls={impuls}")
                if 0 <= impuls <= 0xFFFF:
                    data_bytes = impuls.to_bytes(2, byteorder='little')
                    await self.client.write_gatt_char(char_specifier=CHARACTERISTIC_IMPULS_SET_UUID, data=data_bytes, response=True)
                else:
                    raise ValueError("Invalid data value. Value must be between 0 and 65535.")
        except Exception as e:
            logger.error(f"wd_set_impuls - Error: {e}")
            raise Exception("BLE write error") from e

    async def wd_run_on(self):
        self.check_if_ready()

        logger.info("wd_run_on")
        try:
            await self.client.write_gatt_char(char_specifier=CHARACTERISTIC_RUN_UUID, data=b'\x01', response=True)
        except Exception as e:
            logger.error(f"wd_run_on - Error: {e}")
            raise Exception("BLE write error") from e

    async def wd_run_off(self):
        self.check_if_ready()

        try:
            if self.client is not None:
                logger.info("wd_run_off")
                await self.client.write_gatt_char(char_specifier=CHARACTERISTIC_RUN_UUID, data=b'\x00', response=True)
        except Exception as e:
            logger.error(f"wd_run_off - Error: {e}")
            raise Exception("BLE write error") from e

    async def wd_identify_on(self):
        self.check_if_ready()

        try:
            if self.client is not None:
                logger.info("wd_identify_on")
                await self.client.write_gatt_char(char_specifier=CHARACTERISTIC_IDENTIFY_UUID, data=b'\x01', response=True)
        except Exception as e:
            logger.error(f"wd_identify_on - Error: {e}")
            raise Exception("BLE write error") from e

    async def wd_identify_off(self):
        self.check_if_ready()

        try:
            if self.client is not None:
                logger.info("wd_identify_off")
                await self.client.write_gatt_char(char_specifier=CHARACTERISTIC_IDENTIFY_UUID, data=b'\x00', response=True)
        except Exception as e:
            logger.error(f"wd_identify_off - Error: {e}")
            raise Exception("BLE write error") from e

    async def wd_on(self):
        self.check_if_ready()

        try:
            if self.client is not None:
                logger.info("wd_on")
                await self.client.write_gatt_char(char_specifier=CHARACTERISTIC_ON_OFF_UUID, data=b'\x01', response=True)
        except Exception as e:
            logger.error(f"wd_on - Error: {e}")
            raise Exception("BLE write error") from e

    async def wd_off(self):
        self.check_if_ready()

        try:
            if self.client is not None:
                logger.info("wd_off")
                await self.client.write_gatt_char(char_specifier=CHARACTERISTIC_ON_OFF_UUID, data=b'\x00', response=True)
        except Exception as e:
            logger.error(f"wd_off - Error: {e}")
