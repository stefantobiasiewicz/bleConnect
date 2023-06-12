import os
import json

from mqtt.model import MQTTConnectionDTO


class MQTTConfigManager:
    def __init__(self, folder_path):
        self.file_path = os.path.join(folder_path, 'mqtt.json')
        self.config = None

        # Sprawdzanie, czy plik istnieje
        if os.path.exists(self.file_path):
            self.load_config()
        else:
            self.config = MQTTConnectionDTO()  # Inicjalizacja pustej konfiguracji
            self.save_config()

    def load_config(self):
        with open(self.file_path, 'r') as file:
            data = json.load(file)
            self.config = MQTTConnectionDTO(**data)

    def save_config(self):
        if self.config is not None:
            with open(self.file_path, 'w') as file:
                json.dump(self.config.__dict__, file, indent=4)

    def get_config(self):
        return self.config

    def update_config(self, new_config: MQTTConnectionDTO):
        self.config = new_config
        self.save_config()
