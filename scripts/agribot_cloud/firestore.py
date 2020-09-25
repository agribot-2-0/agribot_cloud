import datetime

import firebase_admin
from firebase_admin import firestore


class Firestore:
    def __init__(self, certificate_file, event):
        self.callback_done = event
        self.certificate_file = certificate_file
        self.database = None
        self.send_sms = None
        self.actual_task_listeners = {}
        self.initialize()

    def initialize(self):
        cred = firebase_admin.credentials.Certificate(self.certificate_file)
        firebase_admin.initialize_app(cred, {'projectID': 'agribot-cd437'})
        self.database = firestore.client()

    def listen_on_actual_task_change(self, send_sms_function):
        self.send_sms = send_sms_function
        robots = self.database.collection(u'robots').stream()
        for robot in robots:
            actual_task_ref = self.database.collection(u'robots').document(
                robot.id)
            self.actual_task_listeners[robot.id] = actual_task_ref.on_snapshot(
                self.actual_task_callback)

    def actual_task_callback(self, doc_snapshot, changes, read_time):  # pylint: disable=unused-argument,no-self-use
        for change in changes:
            if change.type.name == 'ADDED' or change.type.name == 'MODIFIED':
                actual_task_name = change.document.to_dict()['actual_task']
                if actual_task_name:
                    router_number = change.document.to_dict()['router_number']
                    tasks_ref = self.database.collection(u'robots').document(
                        change.document.id).collection(u'tasks').stream()
                    for task in tasks_ref:
                        if task.id == actual_task_name and self.send_sms is not None:
                            self.print_log(actual_task_name, router_number)
                            self.send_sms(router_number, task.to_dict())

        self.callback_done.set()

    @staticmethod
    def print_log(actual_task_name, router_number):
        print("{:<100}".format("-" * 100))
        print("|{:<20} | {:<77}|".format(
            "date",
            datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")))
        print("|{:<20} | {:<77}|".format("actual_task_name", actual_task_name))
        print("|{:<20} | {:<77}|".format("router_number", router_number))
