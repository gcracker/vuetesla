#!/bin/python

import asyncio
import json
import logging
import time
from pyemvue import PyEmVue
from pyemvue.enums import Scale, Unit
from tesla_api import TeslaApiClient, ApiError
import queue

from secrets import Secrets

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s', )
jsonFile = "/home/gprice/keys.json"
BUF_SIZE = 10
q = queue.Queue(BUF_SIZE)
home_queue = queue.Queue(BUF_SIZE)

_LOGGER = logging.getLogger()
logging.basicConfig(level=logging.INFO)

auth = Secrets()

async def teslaWake(leaTesla):
    if leaTesla.state != 'online':
        pass

def getEnergyTotal(vue):
    channel_usage_list = vue.get_recent_usage(scale=Scale.SECOND.value, unit=Unit.WATTS.value)
    for channel in channel_usage_list:
        print(channel.name + " : " + channel.usage)

def getPyEm():
    vue = PyEmVue()
    with open(jsonFile) as f:
        data = json.load(f)
        if 'password' in data:
            vue.login(username=data['email'], password=data['password'], token_storage_file=jsonFile)
        else:
            vue.login(id_token=data['idToken'],
                     access_token=data['accessToken'],
                     refresh_token=data['refreshToken'],
                     token_storage_file=jsonFile)
    return vue


async def getTesla():
    tesClient = None
    leaTesla = None
    charge_port = True

    tesClient = TeslaApiClient(auth.TESLAUSERNAME, auth.TESLAPASSWORD)
    vehicles = await tesClient.list_vehicles()

    try:
        if None is leaTesla:
            if tesClient != None:
                tesClient.close()

            tesClient = TeslaApiClient(auth.TESLAUSERNAME, auth.TESLAPASSWORD)
            vehicles = await tesClient.list_vehicles()

            for v in vehicles:
                if v.vin == '5YJYGDEE9LF035958':
                    leaTesla = v

        if leaTesla.state == 'online':
            try:
                charge = await leaTesla.charge.get_state()

            except Exception as e:
                print("Exception A: " + str(e))
                await tesClient.close()
                leaTesla = None
                tesClient = None
        else:
            await tesClient.close()
            leaTesla = None
            tesClient = None

    except AttributeError as error:
        await tesClient.close()
        tesClient = None
        print(error)


async def main():
    evue = getPyEm()
    getEnergyTotal(evue)

asyncio.run(main())
