import os
import firebase_admin
from firebase_admin import firestore


class Firestore:
    def __init__(self, config):
        self.certificate_file = self.get_certificate_file_path(
            config['certificate_location'], config['certificate_file'])
        self.database = None
        self.send_sms = None
        self.initialize()

    def initialize(self):
        cred = firebase_admin.credentials.Certificate(self.certificate_file)
        firebase_admin.initialize_app(cred, {'projectID': 'agribot-cd437'})
        self.database = firestore.client()

    @staticmethod
    def get_certificate_file_path(file_location, file_name):
        return os.path.join(file_location, file_name)

    def register_on_tasks_change_callback(self, robot_rsn, on_tasks_callback):
        return self.database.collection(u'robots').document(
            robot_rsn).collection(u'tasks').on_snapshot(on_tasks_callback)

    def register_on_robot_change_callback(self, robot_rsn, on_tasks_callback):
        return self.database.collection(u'robots').document(
            robot_rsn).on_snapshot(on_tasks_callback)

    def get_robots_stream(self):
        return self.database.collection(u'robots').stream()

    def get_tasks_stream(self, robot_rsn, order_by=None):
        if order_by is not None:
            return self.database.collection(u'robots').document(
                robot_rsn).collection(u'tasks').order_by(order_by).stream()
        else:
            return self.database.collection(u'robots').document(
                robot_rsn).collection(u'tasks').stream()

    def get_tasks_query(self, robot_rsn):
        return self.database.collection(u'robots').document(
            robot_rsn).collection(u'tasks')

    def get_actual_task(self, robot_rsn):
        return self.database.collection(u'robots').document(
            robot_rsn).get().to_dict()[u'actual_task']

    def get_router_number(self, robot_rsn):
        return self.database.collection(u'robots').document(
            robot_rsn).get().to_dict()[u'router_number']

    def get_tasks_ordered(self, robot_rsn):
        return self.database.collection(u'robots').document(
            robot_rsn).get().to_dict()[u'tasks_ordered']

    def get_task(self, robot_rsn, task_name):
        return self.database.collection(u'robots').document(
            robot_rsn).collection(u'tasks').document(task_name).get()

    def delete_task(self, robot_rsn, task_name):
        self.database.collection(u'robots').document(robot_rsn).collection(
            u'tasks').document(task_name).delete()

    def sort_tasks(self, robot_rsn):
        return self.get_tasks_query(robot_rsn).order_by(u'start_time')

    def update_tasks_ordered(self, robot_rsn, tasks):
        tasks_array = []
        for task in tasks:
            tasks_array.append(task.id)

        self.database.collection(u'robots').document(robot_rsn).update(
            {u'tasks_ordered': tasks_array})

    def update_actual_task(self, robot_rsn, actual_task_name):
        self.database.collection(u'robots').document(robot_rsn).update(
            {u'actual_task': actual_task_name})
