import os
import time
import threading
import logging
from logging.config import fileConfig

import agribot_cloud

# SMS_API_PL_TOKEN = "AGRIBOT_CONFIGURE_LOCALLY"
SMS_API_PL_TOKEN = "AGRIBOT_CONFIGURE_LOCALLY"
certificate_file = os.path.join(
    "/firebase_key", "agribot-cd437-firebase-adminsdk-ypr8o-5e1109055d.json")

if __name__ == "__main__":
    sms_api = agribot_cloud.SmsApi(SMS_API_PL_TOKEN)
    agribot_firestore = agribot_cloud.Firestore(certificate_file)

    fileConfig('logging_config.conf')
    logger = logging.getLogger()

    event = threading.Event()
    agribot_scheduler = agribot_cloud.AgribotScheduler(agribot_firestore,
                                                       event, logger)
    agribot_wakeuper = agribot_cloud.AgribotWakeuper(agribot_firestore,
                                                     sms_api, event, logger)

    w = agribot_cloud.Weather()
    w.request_current_conditions_data()
    logger.info("{} C".format(w.get_temperature()))
    logger.info("{} %".format(w.get_relative_humidity()))
    logger.info("{} km/h".format(w.get_wind_value()))
    logger.info("{} deg".format(w.get_wind_direction()))
    logger.info("{} hPa".format(w.get_pressure()))
    # agribot_scheduler.run()
    # agribot_wakeuper.run()

    while True:
        time.sleep(0.01)
