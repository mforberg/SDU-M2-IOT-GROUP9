import paho.mqtt.client as mqtt  # pip install paho-mqtt. import the client1
import json
import time


class ClientClass:

    def __init__(self):
        self.broker_address = "broker.hivemq.com"
        self.client = mqtt.Client()  # create new instance
        self.client.connect(self.broker_address)  # connect to broker
        self.client.loop_start()

    def deliver_payload(self, variable, topic):
        message = {
            "var": variable,
            "time": time.time() * 1000
        }
        self.client.publish(topic=topic, payload=json.dumps(message), retain=True)
