from asyncio.tasks import sleep
import time
import threading
import os
import asyncio
import random
import logging
import json

from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device import constant, Message, MethodResponse
from datetime import date, timedelta, datetime



CONNECTION_STRING = os.environ["CONNECTION_STRING"]

def iothub_client_init():
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING, websockets = True)
    return client

def compose_d2c_message():
    temp = random.random()
    humid = random.random()
    response_dict = {'protocol_info': 'websockets', 'temperature': temp, 'humidity': humid}
    return json.dumps(response_dict)

async def main():
    client = iothub_client_init()
    await client.connect()
    while(True):
        time.sleep(4)
        await client.send_message(compose_d2c_message())
        

if __name__ == '__main__':
    asyncio.run(main())
