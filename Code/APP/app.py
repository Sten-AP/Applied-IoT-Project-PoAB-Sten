from flask import Flask, redirect, url_for, render_template, request, session
import sqlite3
import mqtt
import requests

URL = "http://localhost:7000"

app = Flask(__name__)
app.secret_key = "D_89kT,(70e}[!Q`zltx'*1t"

temp_id = "eui-a8610a30373d9301"

mqtt.Init()


def baken_aan():
    param = {"status": 1}
    print(requests.post(f"{URL}/baken/{temp_id}/status", params=param).text)
    mqtt.create_downlink("LA1", temp_id)


def baken_uit():
    param = {"status": 0}
    print(requests.post(f"{URL}/baken/{temp_id}/status", params=param).text)
    mqtt.create_downlink("LA0", temp_id)


@app.route('/', methods=["GET", "POST"])
def main():
    if request.method == "POST":
        if request.form["buttons"] == "1":
            baken_aan()
        else:
            baken_uit()
    bakens = requests.get(f"{URL}/baken").json()
    return render_template('index.html', bakens=bakens)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
