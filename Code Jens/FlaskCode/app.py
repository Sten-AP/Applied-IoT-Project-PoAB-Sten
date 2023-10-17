import json
from datetime import datetime

from flask import Flask, redirect, url_for, render_template, request, session
import sqlite3, sys, bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
import device
import group
import influxdb
import mqtt

app = Flask(__name__)
app.secret_key = "D_89kT,(70e}[!Q`zltx'*1t"

mqtt.Init()


def UpdateDeviceList():
    _devices = device.get_all_devices_data()

    device_id = request.args.get('id')
    selected_device = None
    if device_id:
        selected_device = next((d for d in _devices if str(d.device_id) == device_id), None)

    # If 'selected_device' is None, select the first device
    if selected_device is None and _devices:
        selected_device = _devices[0]

    if "lights" in request.args:
        _lights = request.args["lights"]
        if _lights == "on":
            print("Turning lights on")
            mqtt.create_downlink("LA1", selected_device.device_id)
        elif _lights == "off":
            print("Turning lights off")
            mqtt.create_downlink("LA0", selected_device.device_id)
        elif _lights == "auto":
            print("Turning lights auto")

    return _devices, selected_device


def UpdateGroupList():
    newGroup = request.args.get('new')
    if newGroup:
        group.NewGroup()

    deleteGroup = request.args.get('delete')
    if deleteGroup:
        group.DeleteGroup(deleteGroup)

    _groups = group.get_all_group_data(False)

    group_id = request.args.get('id')
    selected_group = None
    if group_id:
        selected_group = next((g for g in _groups if str(g.group_id) == group_id), None)

        if "device" in request.args:
            _device_id = request.args["device"]
            selected_group.device_ids = selected_group.device_ids + _device_id
            data = influxdb.influxdb_client.Point("groups").tag("id", selected_group.group_id).tag("devices",
                                                                                                   "Test").time(
                datetime.strptime(selected_group.time, "%Y-%m-%d %H:%M:%S.%f%z"))
            print(data)
            influxdb.write_api.write(bucket=influxdb.bucket, org=influxdb.org, record=data)
            print("Updating")

    return _groups, selected_group


def get_db_connection():
    connection = sqlite3.connect("LoRa.db", check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return render_template("login.html")


@app.route('/devices', methods=['GET'])
def devices():
    _devices, selected_device = UpdateDeviceList()
    return render_template("devices.html", devices=_devices, currentDevice=selected_device)


@app.route('/groups', methods=['GET'])
def groups():
    _devices, selected_device = UpdateDeviceList()
    _groups, selected_group = UpdateGroupList()
    return render_template("groups.html", devices=_devices, groups=_groups, currentGroup=selected_group)


@app.route('/header', methods=['GET'])
def header():
    return render_template("header.html")


@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        _devices, selected_device = UpdateDeviceList()
        return render_template("devices.html", devices=_devices, currentDevice=selected_device)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        print(generate_password_hash(password))

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session["permissions"] = user["permissions"]

            _devices, selected_device = UpdateDeviceList()
            return render_template("devices.html", devices=_devices, currentDevice=selected_device)
        else:
            return 'Invalid username or password'

    return render_template("login.html")


if __name__ == '__main__':
    app.run()
