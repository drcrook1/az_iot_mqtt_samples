from asyncio.tasks import sleep
import time
import threading
import os
import asyncio
import random
import logging
import json
import requests

from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device import constant, Message, MethodResponse
from datetime import date, timedelta, datetime
import base64

# CONNECTION_STRING = os.environ["CONNECTION_STRING"]
DEVICE_LIST = json.loads(os.environ["DEVICE_LIST"])
DEVICE_CLIENTS = {}

def iothub_client_init(CONNECTION_STRING = None):
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING, websockets = True)
    return client

def compose_d2c_message():
    temp = random.random()
    humid = random.random()
    response_dict = {'protocol_info': 'websockets', 'temperature': temp, 'humidity': humid, "tags" : ["uplink_sim"]}
    return json.dumps(response_dict)

async def simulate_non_native_uplinks():
    """
    This code randomly picks a device which would be communicating with the gateway and sends a random package.
    The result of this would be the gateway needs to forward the package on to iot hub
    """
    while(True):
        print("beginning uplink")
        device = random.randint(0,2)
        await DEVICE_CLIENTS[DEVICE_LIST[device]["device_id"]]["client"].send_message(compose_d2c_message())
        print("processed uplink")
        await asyncio.sleep(4)

async def send_downlink_to_device(message):
    print("Downlink Received:\n")
    for property in vars(message).items():
        print ("    {0}".format(property))

async def configure_device_clients():
    print("configuring device clients")
    for device in DEVICE_LIST:
        DEVICE_CLIENTS[device["device_id"]] = {"conn_str" : device["conn_str"], "client" : iothub_client_init(CONNECTION_STRING = device["conn_str"])}
        print("client object created")
        await DEVICE_CLIENTS[device["device_id"]]["client"].connect()
        print("client object connected")
        DEVICE_CLIENTS[device["device_id"]]["client"].on_message_received = send_downlink_to_device
        print("configured downlink handler")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(configure_device_clients())
    loop.create_task(simulate_non_native_uplinks())
    loop.run_forever()
