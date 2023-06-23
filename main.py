import asyncio
import logging
import os
from threading import Thread

from flask import Flask, request, jsonify, render_template, redirect

from ble.manager import DeviceManager, Status
from ble.scanner import search_and_return_device
from ble.water_dispenser import WaterDispenser
from db.entity import DeviceEntity, DeviceType
from db.manager import DbManager

from mqtt.manager import MQTTConfigManager
from mqtt.model import MQTTConnectionDTO

logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("DB_PATH")
#DB_PATH = '/Users/stefantobiasiewicz/Documents/Programing/Python/bleConnection/test'
# DB_PATH = os.environ.get("DB_PATH")


DB_PATH = '/Users/stefantobiasiewicz/Documents/Programing/Python/bleConnection/test'

ble_loop = asyncio.new_event_loop()

device_manager = DeviceManager(DbManager(DB_PATH), ble_loop)
mqtt_manager = MQTTConfigManager(DB_PATH)

app = Flask(__name__)


@app.route('/api/ble/search', methods=['POST'])
def search_device():
    future = asyncio.run_coroutine_threadsafe(search_and_return_device(), ble_loop)
    devices = future.result()

    devices_mapped = []
    for dev in devices:
        if not device_manager.check_if_contain(dev.address):
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
    # connected?
    water_dispenser: WaterDispenser = device_manager.get_by_id(device_id).ble

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
    # connected?
    water_dispenser: WaterDispenser = device_manager.get_by_id(device_id).ble

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
    # connected?
    water_dispenser: WaterDispenser = device_manager.get_by_id(device_id).ble

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
    # connected?
    water_dispenser: WaterDispenser = device_manager.get_by_id(device_id).ble

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
    devices = []

    for compose in  device_manager.get_devices():
        devices.append(
            {
                "id": compose.entity.id,
                "name": compose.entity.name,
                "address": compose.entity.address,
                "status": compose.status,
                "type": compose.entity.type,
            }
        )

    return render_template('devices.html', devices=devices)


@app.route('/device/<int:device_id>')
def device_details(device_id):
    device = device_manager.get_by_id(device_id)

    device_manager.connect(device)

    # if device.status is Status.DIS_CONNECTED:
    #     return render_template('device_device_not_available.html')

    return render_template('device_details.html', device=device.entity, status=device.status)


# @@@@@@@@@@@@@@@@@ MQTT @@@@@@@@@@@@@@@@@
@app.route('/mqtt/config', methods=['GET'])
def get_mqtt_config():
    config = mqtt_manager.get_config()
    return render_template('mqtt_config.html', config=config)


@app.route('/mqtt/config', methods=['POST'])
def save_mqtt_config():
    data = request.form.to_dict()
    new_config = MQTTConnectionDTO(**data)
    mqtt_manager.update_config(new_config)
    return redirect(location='/mqtt/config')


@app.route('/mqtt/config/edit', methods=['GET'])
def edit_mqtt_config():
    config = mqtt_manager.get_config()
    return render_template('mqtt_edit_config.html', config=config)


# @@@@@@@@@@@@@@@@@ MQTT @@@@@@@@@@@@@@@@@

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

    # scanning by backend
    future = asyncio.run_coroutine_threadsafe(search_and_return_device(), ble_loop)
    devices = future.result()

    # before app start
    try:
        logger.info('connecting to all devices')
        device_manager.connect_all()
    except Exception as e:
        logger.error(e)

    app.run(port=8000, debug=False)

    try:
        logger.info('disconnection from all devices')
        device_manager.disconnect_all()
    except Exception as e:
        logger.error(e)

    # stopping ble thread
    ble_loop.stop()
    t.join()


    a = 2
    print(a)