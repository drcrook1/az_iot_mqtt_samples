import paho.mqtt.client as mqtt
import os
import base64
import hmac
import urllib.parse
import time
import sastoken

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def create_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    #token = str(sastoken.SasToken(uri = os.environ["IOT_HUB_HOST"], key = os.environ["IOT_HUB_SHARED_ACCESS_KEY"]))
    token = "YOURS"
    user_name = os.environ["IOT_HUB_HOST"] + '/' + os.environ["DEVICE_ID"]
    print(user_name)
    print(token)
    client.username_pw_set(user_name, token)
    client.tls_set("/leafdevice/baltimore.cert")
    client.connect(os.environ["IOT_HUB_HOST"], 8883)
    return client

def run_mqtt_sample(client = None):
    client.loop_start()
    while True:
        try:
            client.publish("/tel/device1", "{ 'temperature': 1 }")            
            time.sleep(4)
        except KeyboardInterrupt:
            print("IoTHubClient sample stopped")
            return
        except:
            print("Unexpected error")
            time.sleep(4)
    return None

if __name__ == '__main__':
    client = create_client()
    run_mqtt_sample(client = client)
