import sklearn
import paho.mqtt.client as mqtt
import os, json # need to install
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from joblib import load
import numpy as np
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--threemodel", help="Soll Modell für NTU, pH und Temperatur genutzt werden", action="store_true")
args = parser.parse_args()

modelpath = "iso_forest.joblib"
if args.threemodel:
    modelpath = "iso_forest3.joblib"
    errormodel = load("error_prediction.joblib")
    feature_names = list(errormodel.feature_names_in_)

# load model
model = load(modelpath)

# connect to influxdb
token = os.environ.get("INFLUXDB_TOKEN")
org = "some_org"
url = f"http://{os.environ.get('INFLUXDB_ADDRESS', 'localhost')}:8086"

write_client = InfluxDBClient(url=url, token=token, org=org)
bucket = os.environ.get("BUCKET")

write_api = write_client.write_api(write_options=SYNCHRONOUS)

# setup mqtt


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("sensors/#")

# The callback for when a PUBLISH message is received from the server.


def preprocess_data(data):
    # Example: extract relevant features from JSON
    processed_data = pd.DataFrame(data, index=[0])
    print(processed_data)
    return processed_data


def on_message(client, userdata, msg):
    def preprocess_data(data):
        # Example: extract relevant features from JSON
        processed_data = pd.DataFrame(data, index=[0])
        print(processed_data)
        return processed_data
    try: 
        data = json.loads(msg.payload.decode("utf-8"))
        preprocessed_data = preprocess_data(data)
        # Use the model for prediction
        prediction = model.predict(preprocessed_data)
        p = Point("prediction").field("prediction", prediction[0])
        if args.threemodel:
            preprocessed_data = preprocessed_data[feature_names]
            err = errormodel.predict(preprocessed_data)
            print(err)
            p = Point("prediction").field("prediction", prediction[0]).field("error", err[0])
        write_api.write(bucket=bucket, org=org, record=p)
        print("Received data:", data)
        print("Prediction:", prediction)
    except json.JSONDecodeError:
        print("Received message is not in JSON format.")




mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect(os.environ.get("MQTT_ADDRESS", 'localhost'), 1883, 60)

mqttc.subscribe("sensors/#")

mqttc.loop_forever()