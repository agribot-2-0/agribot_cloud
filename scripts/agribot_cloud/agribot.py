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
    # pylint: disable=too-few-public-methods
    def __init__(self, configs_location):
        fileConfig(os.path.join(configs_location, 'logging.conf'))
        self.logger = logging.getLogger()

        sms_api_config = yaml.load(open(
            os.path.join(configs_location, 'sms_api_pl.yaml')),
                                   Loader=yaml.FullLoader)
        sms_api = SmsApi(sms_api_config, self.logger)

        firebase_config = yaml.load(open(
            os.path.join(configs_location, 'firebase.yaml')),
                                    Loader=yaml.FullLoader)
        agribot_firestore = Firestore(firebase_config)

        weather_config = yaml.load(open(
            os.path.join(configs_location, 'weather.yaml')),
                                   Loader=yaml.FullLoader)
        weather_forecast = Weather(weather_config, self.logger)

        event = threading.Event()
        self.agribot_scheduler = AgribotScheduler(agribot_firestore,
                                                  weather_forecast, event,
                                                  self.logger)
        self.agribot_wakeuper = AgribotWakeuper(agribot_firestore, sms_api,
                                                event, self.logger)

    def run(self, robot_rsn):
        self.logger.info("Agribot Cloud for {} is running".format(robot_rsn))
        self.agribot_scheduler.run(robot_rsn)
        self.agribot_wakeuper.run(robot_rsn)

        while True:
            time.sleep(0.01)
