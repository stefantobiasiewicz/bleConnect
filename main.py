import asyncio
import logging
import os
from threading import Thread

from flask import Flask, request, jsonify, render_template

from ble.manager import DeviceManager
from ble.scanner import search_and_return_device
from ble.water_dispenser import WaterDispenser
from db.entity import DeviceEntity, DeviceType
from db.manager import DbManager

# DB_PATH = os.environ.get("DB_PATH")
DB_PATH = '/Users/stefantobiasiewicz/Documents/Programing/Python/bleConnection/test'

ble_loop = asyncio.new_event_loop()

device_manager = DeviceManager(DbManager(DB_PATH), ble_loop)

app = Flask(__name__)


def check_if_contain(manager, devices):
    addresses = []
    for device in manager.get_devices():
        addresses.append(device.address)

    for device in devices:
        if device.address in addresses:
            devices.remove(device)

    return devices


@app.route('/api/ble/search', methods=['POST'])
def search_device():
    future = asyncio.run_coroutine_threadsafe(search_and_return_device(), ble_loop)
    devices = future.result()

    devices_mapped = []
    for dev in devices:
        if device_manager.check_if_contain(dev.address):
            devices_mapped.append({"name": dev.name, "address": dev.address})

    # Tworzenie odpowiedzi JSON
    response = {
        'status': 'success',
        'message': 'Urządzenia zostały znalezione.',
        'devices': devices_mapped
    }

    return jsonify(response)


@app.route('/api/ble/add', methods=['POST'])
def add_ble_device():
    address = request.form.get('address')

    device = DeviceEntity(id=None, address=address, name="nowe urzadzenie", type=DeviceType.WD)

    device_manager.add_device(device)

    response = {
        'id': device.id
    }
    return jsonify(response)


@app.route('/api/ble/<int:device_id>/wd/identify', methods=['POST'])
def wd_identify(device_id: int):
    value = int(request.form.get('value'))

    # isinstance?
    water_dispenser: WaterDispenser = device_manager.get_device_by_id(device_id)

    if water_dispenser is None:
        return jsonify({'status' : 'no-device'})

    if value == 1:
        water_dispenser.wd_identify_on()
    else:
        water_dispenser.wd_identify_off()

    response = {
        'status': "good"
    }
    return jsonify(response)


@app.route('/api/ble/<int:device_id>/wd/onoff', methods=['POST'])
def wd_on_off(device_id: int):
    value = int(request.form.get('value'))

    # isinstance?
    water_dispenser: WaterDispenser = device_manager.get_device_by_id(device_id)

    if water_dispenser is None:
        return jsonify({'status' : 'no-device'})

    if value == 1:
        water_dispenser.wd_on()
    else:
        water_dispenser.wd_off()

    response = {
        'status': "good"
    }
    return jsonify(response)


@app.route('/api/ble/<int:device_id>/wd/impuls', methods=['POST'])
def wd_impuls(device_id: int):
    value = int(request.form.get('value'))

    # isinstance?
    water_dispenser: WaterDispenser = device_manager.get_device_by_id(device_id)


    if water_dispenser is None:
        return jsonify({'status' : 'no-device'})

    water_dispenser.wd_set_impuls(value)

    response = {
        'status': "good"
    }
    return jsonify(response)


@app.route('/api/ble/<int:device_id>/wd/run', methods=['POST'])
def wd_run(device_id: int):
    value = int(request.form.get('value'))

    # isinstance?
    water_dispenser: WaterDispenser = device_manager.get_device_by_id(device_id)


    # some advisor?
    if water_dispenser is None:
        return jsonify({'status' : 'no-device'})

    if value == 1:
        water_dispenser.wd_run_on()
    else:
        water_dispenser.wd_run_off()

    response = {
        'status': "good"
    }
    return jsonify(response)


@app.route('/', methods=['GET'])
def devices():
    return render_template('devices.html', devices=device_manager.get_devices())


@app.route('/device/<int:device_id>')
def device_details(device_id):
    device = device_manager.get_entity_by_id(device_id)
    try:
        device_manager.get_connected_device_by_id(device_id)

        return render_template('device_details.html', device=device)
    except Exception as e:
        print(f'Wystąpił wyjątek: {str(e)}')
        # client_manager.remove_by_address(device.address)
        return render_template('device_device_not_available.html')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # special thread for bleak
    def bleak_thread(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()
        a = 2
        print(a)

    t = Thread(target=bleak_thread, args=(ble_loop,))
    t.start()

    # before app start
    device_manager.connect_all()

    app.run(port=8000, debug=False)

    # stopping ble thread
    ble_loop.stop()
    t.join()

    a = 2
    print(a)