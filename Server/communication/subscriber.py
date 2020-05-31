import paho.mqtt.client as mqtt  # pip install paho-mqtt
import time
import json


def on_connect(client, userdata, flags, rc):
    client.subscribe("sdu/iot/gruppe9/light")


def on_message(client, userdata, msg):
    time_after = time.time() * 1000
    print(msg.payload)
    msg_dict = json.loads(msg.payload.decode('utf-8'))
    msg_dict["timeAfter"] = time_after
    with open("data.csv", "a") as file:
        print(json.dumps(msg_dict))
        file.write(json.dumps(msg_dict) + "\n")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 4)
client.loop_forever()
