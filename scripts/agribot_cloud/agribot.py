import os
import time
import threading
import logging
from logging.config import fileConfig
import yaml

from agribot_cloud.agribot_wakeuper import AgribotWakeuper
from agribot_cloud.agribot_scheduler import AgribotScheduler
from agribot_cloud.sms_api import SmsApi
from agribot_cloud.firestore import Firestore
from agribot_cloud.weather import Weather


class AgribotCloud:
    def __init__(self, configs_location):
        fileConfig(os.path.join(configs_location, 'logging.conf'))
        logger = logging.getLogger()

        sms_api_config = yaml.load(open(
            os.path.join(configs_location, 'sms_api_pl.yaml')),
                                   Loader=yaml.FullLoader)
        sms_api = SmsApi(sms_api_config, logger)

        firebase_config = yaml.load(open(
            os.path.join(configs_location, 'firebase.yaml')),
                                    Loader=yaml.FullLoader)
        agribot_firestore = Firestore(firebase_config)

        weather_config = yaml.load(open(
            os.path.join(configs_location, 'weather.yaml')),
                                   Loader=yaml.FullLoader)
        weather = Weather(weather_config, logger)

        event = threading.Event()
        self.agribot_scheduler = AgribotScheduler(agribot_firestore, event,
                                                  logger)
        self.agribot_wakeuper = AgribotWakeuper(agribot_firestore, sms_api,
                                                event, logger)

        if weather.request_current_conditions_data():
            logger.info("{} C".format(weather.get_temperature()))
            logger.info("{} %".format(weather.get_relative_humidity()))
            logger.info("{} km/h".format(weather.get_wind_value()))
            logger.info("{} deg".format(weather.get_wind_direction()))
            logger.info("{} hPa".format(weather.get_pressure()))

    def run(self):
        self.agribot_scheduler.run()
        self.agribot_wakeuper.run()

        while True:
            time.sleep(0.01)
