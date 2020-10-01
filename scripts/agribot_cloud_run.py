import os
import time
import threading

import agribot_cloud

# SMS_API_PL_TOKEN = "AGRIBOT_CONFIGURE_LOCALLY"
SMS_API_PL_TOKEN = "AGRIBOT_CONFIGURE_LOCALLY"
certificate_file = os.path.join(
    "/firebase_key", "agribot-cd437-firebase-adminsdk-ypr8o-5e1109055d.json"
)


if __name__ == "__main__":
    sms_api = agribot_cloud.SmsApi(SMS_API_PL_TOKEN)
    firestore = agribot_cloud.Firestore(certificate_file, threading.Event())

    agribot_wakeuper = agribot_cloud.AgribotWakeuper(firestore, sms_api)
    agribot_wakeuper.run()

    while True:
        time.sleep(0.01)
