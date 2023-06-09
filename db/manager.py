import os
import json

from db.entity import DeviceEntity


class DbManager:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.file_path = os.path.join(folder_path, 'devices.json')
        self.devices = []

        # Sprawdzanie, czy plik devices.json istnieje
        if os.path.exists(self.file_path):
            self.load_devices()
        else:
            self.save_devices()

    def load_devices(self):
        with open(self.file_path, 'r') as file:
            data = json.load(file)
            self.devices = [DeviceEntity(**device) for device in data]

    def save_devices(self):
        data = [device.__dict__ for device in self.devices]
        with open(self.file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def add_device(self, device: DeviceEntity):
        if device.id is None:
            device.id = self.generate_next_id()

        if self.is_address_unique(device.address):
            self.devices.append(device)
            self.save_devices()
            return device
        else:
            raise ValueError('Address must be unique')

    def remove_device(self, device):
        self.devices.remove(device)
        self.save_devices()

    def get_devices(self):
        return self.devices

    def get_devices_by_id(self, id) -> DeviceEntity:
        for device in self.devices:
            if device.id == id:
                return device
        return None

    def generate_next_id(self):
        if self.devices:
            last_device = max(self.devices, key=lambda d: d.id)
            return last_device.id + 1
        return 1

    def is_address_unique(self, address):
        for device in self.devices:
            if device.address == address:
                return False
        return True
