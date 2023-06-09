import asyncio

from flask import render_template

from db.entity import DeviceType
from main import app, db_manager, device_manager

class Views:
    def __init__(self):
        pass

    @app.route('/', methods=['GET'])
    def devices(self):
        return render_template('devices.html', devices=db_manager.get_devices())


    @app.route('/device/<int:device_id>')
    def device_details(slef, device_id):
        device = db_manager.get_device_by_id(device_id)
        try:
            if device.type is not DeviceType.TEST:
                ble_device = device_manager.read_device(device)
                if not ble_device.client.is_connected:
                    future = asyncio.run_coroutine_threadsafe(ble_device.client.connect(), ble_loop)
                    future.result()

            return render_template('device_details.html', device=device)
        except Exception as e:
            print(f'Wystąpił wyjątek: {str(e)}')
            # client_manager.remove_by_address(device.address)
            return render_template('device_device_not_available.html')