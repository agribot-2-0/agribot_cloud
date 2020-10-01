import os
import pathlib
import time
import threading

import agribot_cloud

#SMS_API_PL_TOKEN = "AGRIBOT_CONFIGURE_LOCALLY"
SMS_API_PL_TOKEN = "AGRIBOT_CONFIGURE_LOCALLY"
certificate_file = os.path.join(
    str(pathlib.Path.home()),
    "agribot-cd437-firebase-adminsdk-ypr8o-5e1109055d.json")

sms_api = agribot_cloud.SmsApi(SMS_API_PL_TOKEN)
agribot_firestore = agribot_cloud.Firestore(certificate_file)

event = threading.Event()
agribot_scheduler = agribot_cloud.AgribotScheduler(agribot_firestore, event)
agribot_wakeuper = agribot_cloud.AgribotWakeuper(agribot_firestore, sms_api,
                                                 event)

agribot_scheduler.run()
agribot_wakeuper.run()

while True:
    time.sleep(0.01)
