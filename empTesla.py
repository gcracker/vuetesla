#!/bin/python

import asyncio
import json
import logging
import queue

from pyemvue import PyEmVue
from pyemvue.enums import Scale, Unit
from tesla_api import TeslaApiClient

from secrets import Secrets

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s', )
json_file = "keys.json"
token_file = "token.txt"
_LOGGER = logging.getLogger()
logging.basicConfig(level=logging.INFO)

auth = Secrets()


async def tesla_wake(my_tesla):
    if my_tesla.state != 'online':
        pass


def get_energy_total(vue):
    channel_usage_list = vue.get_recent_usage(scale=Scale.SECOND.value, unit=Unit.WATTS.value)
    for channel in channel_usage_list:
        print(channel.name + " : " + channel.usage)


def get_vue():
    vue = PyEmVue()

    try:
        data = json.load(json_file)
    except:
        return None

    try:
        vue.login(username=data['email'], password=data['password'], token_storage_file=token_file)
    except:
        try:
            vue.login(id_token=data['idToken'],
                    access_token=data['accessToken'],
                    refresh_token=data['refreshToken'],
                    token_storage_file=json_file)
        except:
            return None
    return vue

async def get_tesla():
    tesla_client = None
    my_tesla = None
    charge_port = True

    tesla_client = TeslaApiClient(auth.TESLAUSERNAME, auth.TESLAPASSWORD)
    vehicles = await tesla_client.list_vehicles()

    try:
        if None is my_tesla:
            if tesla_client is not None:
                tesla_client.close()

            tesla_client = TeslaApiClient(auth.TESLAUSERNAME, auth.TESLAPASSWORD)
            vehicles = await tesla_client.list_vehicles()

            for v in vehicles:
                if v.vin == '5YJYGDEE9LF035958':
                    my_tesla = v

        if my_tesla.state == 'online':
            try:
                charge = await my_tesla.charge.get_state()

            except Exception as e:
                print("Exception A: " + str(e))
                await tesla_client.close()
                my_tesla = None
                tesla_client = None
        else:
            await tesla_client.close()
            my_tesla = None
            tesla_client = None

    except AttributeError as error:
        await tesla_client.close()
        tesla_client = None
        print(error)


async def main():
    evue = get_vue()
    get_energy_total(evue)


asyncio.run(main())
