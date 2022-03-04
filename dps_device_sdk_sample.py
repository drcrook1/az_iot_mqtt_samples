from asyncio.tasks import sleep
import time
import threading
import os
import asyncio
import random
import logging
import json
import requests
import hmac
import hashlib
import urllib

from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device import constant, Message, MethodResponse
from datetime import date, timedelta, datetime
import base64
import time

DEVICE_CLIENT = None

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
        await DEVICE_CLIENT.send_message(compose_d2c_message())
        print("processed uplink")
        await asyncio.sleep(5)

def get_dps_sas_auth_header(scope_id, device_id, key):
    sr = "{}%2Fregistrations%2F{}".format(scope_id, device_id)
    expires = int(time.time() + (7200)) #
    registration_id = f"{sr}\n{str(expires)}"
    secret = base64.b64decode(key) 
    signature = base64.b64encode(
        hmac.new(
            secret, msg=registration_id.encode("utf8"), digestmod=hashlib.sha256
        ).digest()
    )
    quote_signature = urllib.parse.quote(signature, "~()*!.'")
    token = f"SharedAccessSignature sr={sr}&sig={quote_signature}&se={str(expires)}&skn=registration"    
    return token

def request_provision(dps_scope_id = "", device_key = "", device_id = "") -> str:
    auth_token = get_dps_sas_auth_header(dps_scope_id, device_id, device_key)
    # Showcase Rest API, because some folks are using unsupported languages.
    url = "https://global.azure-devices-provisioning.net/{}/registrations/{}/register?api-version=2019-03-31".format(
        dps_scope_id, device_id
    )
    header_parameters = {
        "Content-Type": "application/json",
        "Authorization": auth_token,
    }
    body = {"registrationId": "{}".format(device_id)}
    response = requests.put(url, headers=header_parameters, json=body)
    return response

def check_provision_status(operation_id = "", dps_scope_id = "", device_key = "", device_id = "") -> str:
    auth_token = get_dps_sas_auth_header(dps_scope_id, device_id, device_key)
    # Showcase Rest API, because some folks are using unsupported languages.
    url = "https://global.azure-devices-provisioning.net/{}/registrations/{}/operations/{}?api-version=2021-06-01".format(
        dps_scope_id, device_id, operation_id
    )
    header_parameters = {
        "Content-Type": "application/json",
        "Authorization": auth_token,
    }
    response = requests.get(url, headers=header_parameters)    
    return response

def compose_iot_hub_str(response_object = None, device_key = None) -> str:
    IOTHUB_BASE_CONN_STR = "HostName={};DeviceId={};SharedAccessKey={}"    
    response_body = response_object.json()
    return IOTHUB_BASE_CONN_STR.format(response_body["registrationState"]["assignedHub"], response_body["registrationState"]["deviceId"], device_key)

def get_iothub_conn_str(dps_scope_id = "", device_key = "", device_id = "") -> str:
    """
    """
    response = request_provision(dps_scope_id=dps_scope_id, device_key=device_key, device_id=device_id)
    if(response.status_code == 202):
        time.sleep(int(response.headers["Retry-After"]) + 1)
        while(True):
            check_response = check_provision_status(operation_id = response.json()["operationId"], dps_scope_id = dps_scope_id, device_key = device_key, device_id = device_id)
            if(check_response.status_code == 200):
                return compose_iot_hub_str(check_response, device_key=device_key)
            elif(check_response.status_code == 202):
                time.sleep(int(response.headers["Retry-After"]) + 1)
            else:
                raise Exception("Something bad happened.")
    elif(response.status_code == 200):
        return compose_iot_hub_str(response, device_key=device_key)
    else:
        raise Exception("Something bad happened.")

def iothub_client_init(conn_str = None):
    client = IoTHubDeviceClient.create_from_connection_string(conn_str, websockets = True)
    return client

async def configure_device_client():
    conn_str = get_iothub_conn_str(dps_scope_id = "0ne00428668", device_key = "vqtB9rWiZm38VLj5E/u014sZlgtqoPWZyNAVBluFJyM=", device_id = "19br1otrp04")
    global DEVICE_CLIENT
    DEVICE_CLIENT = iothub_client_init(conn_str=conn_str)
    await DEVICE_CLIENT.connect()
    print("did it work?")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(configure_device_client())
    loop.create_task(simulate_non_native_uplinks())
    loop.run_forever()