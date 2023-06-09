from typing import Dict

from bleak import BleakClient

from ble.water_dispenser import BleDevice, WaterDispenser
from db.entity import DeviceEntity, DeviceType
from db.manager import DbManager


class DeviceManager:
    def __init__(self, db_manager: DbManager, loop):
        self.device_map: Dict[DeviceEntity, BleDevice] = {}
        self.ble_loop = loop
        self.db_manager = db_manager
        self.db_manager.load_devices()

        devices = self.db_manager.get_devices()
        for device in devices:
            self._create_device(device)



    def add_device(self, device: DeviceEntity) -> BleDevice:
        added_device = self.db_manager.add_device(device)
        if added_device is not None:
            self._create_device(added_device)
        return self.device_map[added_device]

    def remove_device(self, device):
        self.db_manager.remove_device(device)
        self.remove_device(device)

    def get_devices(self) -> [DeviceEntity]:
        return list(self.device_map.keys())

    def get_device_by_id(self, id) -> BleDevice:
        return self.device_map[self.db_manager.get_devices_by_id(id)]

    def get_connected_device_by_id(self, id) -> BleDevice:
        entity = self.db_manager.get_devices_by_id(id)
        device = self.device_map[entity]

        self.connect_device(entity, device)

        return device

    def get_entity_by_id(self, id) -> DeviceEntity:
        return self.db_manager.get_devices_by_id(id)


    def _create_device(self, device_entity: DeviceEntity):
        if device_entity in self.device_map:
            return

        ble_device: BleDevice = None

        if device_entity.type == DeviceType.WD:
            client = BleakClient(address_or_ble_device=device_entity.address,
                                 disconnected_callback=self.disconnect)
            ble_device = WaterDispenser(client=client, loop=self.ble_loop)
        else:
            return

        self.device_map[device_entity] = ble_device

    def connect_device(self, entity: DeviceEntity, ble_device: BleDevice):
        entity.status = 'disconnected'

        if entity.type == DeviceType.TEST:
            return

        if not ble_device.is_connected:
            try:
                ble_device.connect()
                entity.status = 'connected'
            except Exception as e:
                entity.status = 'disconnected'
                return

        entity.status = 'connected'

    def connect_all(self):
        for entity, ble_device in self.device_map.items():
            self.connect_device(entity, ble_device)

    def check_if_contain(self, address: str) -> bool:
        is_contain = False
        for entity, ble_device in self.device_map.items():
            if ble_device.client.address == address:
                is_contain = True
                return is_contain
        return is_contain

    def disconnect(self, client: BleakClient):
        device_entity = None
        for entity, ble in self.device_map.items():
            if ble.client == client:
                device_entity = entity

        device_entity.status = 'disconnected'


