from enum import Enum
from typing import Dict

from bleak import BleakClient

from ble.water_dispenser import BleDevice, WaterDispenser
from db.entity import DeviceEntity, DeviceType
from db.manager import DbManager


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
                                 disconnected_callback=self.disconnect)
            ble_device = WaterDispenser(client=client, loop=self.ble_loop)
        else:
            return

        compose = DeviceCompose(device_entity, ble_device)

        self.device_list.append(compose)

    def connect(self, compose: DeviceCompose):
        compose.status = 'disconnected'

        if compose.entity.type == DeviceType.TEST:
            return

        if not compose.ble.is_connected:
            try:
                compose.ble.connect()
                compose.status = 'connected'
            except Exception as e:
                compose.status = 'disconnected'
                return

        compose.status = 'connected'

    def connect_all(self):
        for compose in self.device_list:
            self.connect(compose)

    def check_if_contain(self, address: str) -> bool:
        is_contain = False
        for compose in self.device_list:
            if compose.ble.client.address == address:
                is_contain = True
                return is_contain
        return is_contain

    def disconnect(self, client: BleakClient):
        compose_founded = None
        for compose in self.device_list:
            if compose.ble.client == client:
                compose_founded = compose

        compose_founded.status = 'disconnected'


