from flask import Flask, render_template, request, jsonify, url_for
import paho.mqtt.client as mqtt
from threading import Thread, Event
import time
from util.utils import generate_json
import json
import os

app = Flask(__name__)

# MQTT settings
MQTT_BROKER = os.environ.get("MQTT", "localhost")  # Replace with your MQTT broker address
MQTT_PORT = 1883
MQTT_TOPIC = "sensors/test/ph-ntu-temp"

# Shared state for the message
message = "0"
stop_event = Event()



def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# MQTT client setup
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)


def publish_message():
    while not stop_event.is_set():
        if message == "0":
            # Normalzustand
            temp_range = (25, 30)   # °C
            ph_range = (7, 8)       # pH
            ntu_range = (0, 10)  # NTU
        elif message == "1":
            # Kontamination
            temp_range = (25, 30)   # °C
            ph_range = (8.1, 11)       # pH
            ntu_range = (30, 40)  # NTU
        elif message == "2":
            # Alte Lösung
            temp_range = (25, 30)   # °C
            ph_range = (3.5, 6.9)       # pH
            ntu_range = (20, 30)  # NTU
        elif message == "3":
            # Falsche Dosierung
            temp_range = (25, 30)   # °C
            ph_range = (3.5, 6.9)       # pH
            ntu_range = (15, 30)  # NTU
        elif message == "4":
            # Temperaturproblem
            temp_range = (30, 35)   # °C
            ph_range = (7.5, 8.5)       # pH
            ntu_range = (15, 20)  # NTU
        else:
            temp_range = (25, 30)   # °C
            ph_range = (7, 8)       # pH
            ntu_range = (0, 10)  # NTU
        data = generate_json(temp_range=temp_range,
                             ntu_range=ntu_range,
                             ph_range=ph_range)
        mqtt_client.publish(MQTT_TOPIC, json.dumps(data))
        print(f"Publishing sensor_data: {data}")
        time.sleep(5)


@app.route('/send', methods=['POST'])
def send():
    global message
    data = request.get_json()
    message = data.get("value")
    print(message)
    return jsonify({"message": "Success"})


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        print(request.form)
    return render_template("index.html")


if __name__ == '__main__':
    # Start the MQTT publishing thread
    publish_thread = Thread(target=publish_message)
    publish_thread.start()
    try:
        app.run(debug=True, use_reloader=False, port=5001, host="0.0.0.0")
    finally:
        stop_event.set()
        publish_thread.join()