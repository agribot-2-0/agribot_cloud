import time
import threading
import logging
from logging.config import fileConfig
import yaml

import agribot_cloud

if __name__ == "__main__":
    fileConfig('/configs/logging.conf')
    logger = logging.getLogger()

    sms_api_config = yaml.load(open("/configs/sms_api_pl.yaml"),
                               Loader=yaml.FullLoader)
    sms_api = agribot_cloud.SmsApi(sms_api_config, logger)

    firebase_config = yaml.load(open("/configs/firebase.yaml"),
                                Loader=yaml.FullLoader)
    agribot_firestore = agribot_cloud.Firestore(firebase_config)

    event = threading.Event()
    agribot_scheduler = agribot_cloud.AgribotScheduler(agribot_firestore,
                                                       event, logger)
    agribot_wakeuper = agribot_cloud.AgribotWakeuper(agribot_firestore,
                                                     sms_api, event, logger)

    # w = agribot_cloud.Weather()
    # w.request_current_conditions_data()
    # logger.info("{} C".format(w.get_temperature()))
    # logger.info("{} %".format(w.get_relative_humidity()))
    # logger.info("{} km/h".format(w.get_wind_value()))
    # logger.info("{} deg".format(w.get_wind_direction()))
    # logger.info("{} hPa".format(w.get_pressure()))
    agribot_scheduler.run()
    agribot_wakeuper.run()

    while True:
        time.sleep(0.01)
