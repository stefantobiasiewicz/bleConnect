import asyncio
import logging
from enum import Enum
from typing import Dict

from bleak import BleakClient
from bleak.exc import BleakDeviceNotFoundError
from retry import retry

from ble.scanner import search_and_return_device
from ble.water_dispenser import BleDevice, WaterDispenser
from db.entity import DeviceEntity, DeviceType
from db.manager import DbManager

logger = logging.getLogger(__name__)

class Status(str, Enum):
    CONNECTED = "connected"
    DIS_CONNECTED = "disconnected"

class DeviceCompose:
    def __init__(self, entity: DeviceEntity, ble: BleDevice):
        self.entity: DeviceEntity = entity
        self.ble: BleDevice = ble
        self.status: Status = Status.DIS_CONNECTED


class DeviceManager:
    def __init__(self, db_manager: DbManager, loop):
        self.device_list: list[DeviceCompose] = []
        self.ble_loop = loop
        self.db_manager = db_manager
        self.db_manager.load_devices()

        devices = self.db_manager.get_devices()
        for device in devices:
            self._create_device(device)

    def get_by_id(self, id: int) -> DeviceCompose:
        for device in self.device_list:
            if device.entity.id == id:
                return device
        return None

    def get_by_client(self, client: BleakClient) -> DeviceCompose:
        for device in self.device_list:
            if device.ble.client == client:
                return device
        return None

    def get_by_entity(self, entity: DeviceEntity) -> DeviceCompose:
        for device in self.device_list:
            if device.entity == entity:
                return device
        return None



    def add_device(self, device: DeviceEntity) -> DeviceCompose:
        added_device = self.db_manager.add_device(device)
        if added_device is not None:
            self._create_device(added_device)
        return self.get_by_entity(added_device)

    def remove_device(self, device):
        self.db_manager.remove_device(device)
        self.remove_device(device)

    def get_devices(self) -> [DeviceCompose]:
        return self.device_list



    def _create_device(self, device_entity: DeviceEntity):
        if self.get_by_entity(device_entity) is not None:
            return

        ble_device: BleDevice = None

        if device_entity.type == DeviceType.WD:
            client = BleakClient(address_or_ble_device=device_entity.address,
                                 disconnected_callback=self.disconnect_callback)
            ble_device = WaterDispenser(client=client, loop=self.ble_loop)
        elif device_entity.type == DeviceType.TEST:
            ble_device = None
        else:
            return

        compose = DeviceCompose(device_entity, ble_device)

        self.device_list.append(compose)

    @retry(exceptions=Exception, tries=3)
    def connect(self, compose: DeviceCompose):
        compose.status = 'disconnected'

        if compose.entity.type == DeviceType.TEST:
            return

        logger.info(f'connecting to {compose} with status: {compose.ble.is_connected}.')

        if not compose.ble.is_connected:
            try:
                logger.info(f'trying to connect by ble stack.')
                compose.ble.connect()
                compose.status = 'connected'
            except BleakDeviceNotFoundError as e:
                logger.info(f'error BleakDeviceNotFoundError trying to connect one more time.')
                asyncio.run_coroutine_threadsafe(search_and_return_device(), self.ble_loop).result()

                compose.ble.connect()
                compose.status = 'connected'
            except Exception as e:

                compose.status = 'disconnected'
                raise Exception(e)

        compose.status = 'connected'

    def disconnect(self, compose: DeviceCompose):
        compose.status = 'disconnected'

        if compose.entity.type == DeviceType.TEST:
            return

        if compose.ble.is_connected:
            compose.ble.disconnect()


    def connect_all(self):
        for compose in self.device_list:
            self.connect(compose)

    def disconnect_all(self):
        for compose in self.device_list:
            self.disconnect(compose)

    def check_if_contain(self, address: str) -> bool:
        is_contain = False
        for compose in self.device_list:
            if compose.entity.type == DeviceType.TEST:
                return False
            if compose.ble.client.address == address:
                is_contain = True
                return is_contain
        return is_contain

    def disconnect_callback(self, client: BleakClient):
        compose_founded = None
        for compose in self.device_list:
            if compose.entity.type is DeviceType.TEST:
                continue
            if compose.ble.client == client:
                compose_founded = compose

        compose_founded.status = 'disconnected'


