from enum import Enum


class DeviceType(str, Enum):
    WD = "WATER-DISPENSER"
    TEST = "TEST"


class DeviceEntity:
    def __init__(self, id: int, name: str, address: str, type: str):
        self.id: int = id
        self.name: str = name
        self.address: str = address
        self.type: DeviceType = DeviceType(type)
        self.status: str = 'disconnected'


# Przykładowe użycie
model = DeviceEntity(1, "Example Model", "00:11:22:33:44:55", DeviceType.WD)
