import firebase_admin
import threading
import datetime
import time
import os
import pathlib

from smsapi.client import SmsApiPlClient
from firebase_admin import firestore

CALLBACK_DONE = threading.Event()

certificate_file = os.path.join(
    str(pathlib.Path.home()),
    "agribot-cd437-firebase-adminsdk-ypr8o-5e1109055d.json")
#sms_api_pl_token = "AGRIBOT_CONFIGURE_LOCALLY"
sms_api_pl_token = "AGRIBOT_CONFIGURE_LOCALLY"

client = SmsApiPlClient(access_token=sms_api_pl_token)

cred = firebase_admin.credentials.Certificate(certificate_file)
firebase_admin.initialize_app(cred, {'projectID': 'agribot-cd437'})
database = firestore.client()


# Create a callback on_snapshot function to capture changes
def firebase_callback(doc_snapshot, changes, read_time):  # pylint: disable=unused-argument
    for change in changes:
        if change.type.name == 'ADDED' or change.type.name == 'MODIFIED':
            actual_task_name = change.document.to_dict()['actual_task']
            if actual_task_name:
                print("{:<100}".format("-" * 100))
                router_number = change.document.to_dict()['router_number']
                print("|{:<20} | {:<77}|".format(
                    "date",
                    datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")))
                print("|{:<20} | {:<77}|".format("actual_task_name",
                                                 actual_task_name))
                print("|{:<20} | {:<77}|".format("router_number",
                                                 router_number))
                task_ref = database.collection(u'robots').document(
                    change.document.id).collection(u'tasks').stream()
                for task in task_ref:
                    if task.id == actual_task_name:
                        agribot_program(router_number, task.to_dict())

    CALLBACK_DONE.set()


def send_sms(number, message_body):
    send_results = client.sms.send(to=number, message=message_body)

    print("|{:<100}|".format("SMS sent to {}, body {}".format(
        number, message_body)))


# http://stackoverflow.com/q/3844948/
def checkEqualIvo(lst):
    return not lst or lst.count(lst[0]) == len(lst)


def agribot_program(agribot_number, condtions_dict):
    keys = [
        "wind_value", "wind_condition", "temp_value", "temp_condition",
        "press_value", "press_condition", "humidity_value",
        "humidity_condition", "start_time"
    ]
    message_body = []
    for key in keys:
        if key in condtions_dict:
            if key == "start_time":
                message_body.append(
                    str(condtions_dict[key].strftime("%Y-%m-%d-%H:%M")))
            else:
                message_body.append(str(condtions_dict[key]))
        else:
            message_body.append("*")

    if checkEqualIvo(message_body):
        message_body = "startnow"
    else:
        message_body = '#'.join(message_body)
        message_body = 'config ' + message_body
    # print("|{:<20} | {:<20}|".format("sms_body", message_body))
    send_sms(agribot_number, message_body)


def send_task_to_agribot(agribot_rsn):
    actual_task_ref = database.collection(u'robots').document(agribot_rsn)
    actual_task_ref.on_snapshot(firebase_callback)


send_task_to_agribot("ADI75R1")
while True:
    time.sleep(0.01)
