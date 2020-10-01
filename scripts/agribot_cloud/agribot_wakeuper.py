import datetime


class AgribotWakeuper:
    task_keys = [
        "wind_value", "wind_condition", "temperature_value",
        "temperature_condition", "pressure_value", "pressure_condition",
        "humidity_value", "humidity_condition", "start_time"
    ]

    null_program_character = '*'
    start_now_time = "2000-01-01-12:00"

    def __init__(self, firestore, sms_api, event):
        self.callback_done = event
        self.agribot_firestore = firestore
        self.sms_api = sms_api
        self.actual_task_listeners = {}

    def run(self):
        for robot in self.agribot_firestore.get_robots_stream():
            # actual_task_ref = self.agribot_firestore.database.collection(
            #     u'robots').document(robot.id)
            self.actual_task_listeners[
                robot.
                id] = self.agribot_firestore.register_on_robot_change_callback(
                    robot.id, self.actual_task_callback)

    # http://stackoverflow.com/q/3844948/
    # Check if all elements are the same
    @staticmethod
    def check_equal_elements(lst):
        return not lst or lst.count(lst[0]) == len(lst)

    def agribot_program_function(self, agribot_number, condtions_dict):
        message_body = []

        for key in self.task_keys:
            if key in condtions_dict:
                if key == "start_time":
                    message_body.append(
                        self.time_to_string(condtions_dict[key]))
                else:
                    message_body.append(str(condtions_dict[key]))
            else:
                print("|{:<100}|".format(
                    "SMS not send. Task definition is incomplete."))
                return

        if self.check_equal_elements(message_body):
            message_body = "startnow"
        else:
            message_body = '#'.join(message_body)
            message_body = 'config ' + message_body
        self.sms_api.send_sms(agribot_number, message_body)

    def actual_task_callback(self, doc_snapshot, changes, read_time):  # pylint: disable=unused-argument,no-self-use
        print("Wakeuper robot change")
        robot_rsn = doc_snapshot[0].id
        # for change in changes:
        #     if change.type.name == 'ADDED' or change.type.name == 'MODIFIED':
        actual_task_name = self.agribot_firestore.get_actual_task(robot_rsn)
        if actual_task_name:
            router_number = self.agribot_firestore.get_router_number(robot_rsn)
            tasks_ref = self.agribot_firestore.get_tasks_stream(robot_rsn)
            for task in tasks_ref:
                if task.id == actual_task_name:
                    self.print_log(actual_task_name, router_number)
                    self.agribot_program_function(router_number,
                                                  task.to_dict())

        self.callback_done.set()

    def time_to_string(self, time):
        start_time_str = time.strftime("%Y-%m-%d-%H:%M")
        if start_time_str == self.start_now_time:
            start_time_str = self.null_program_character

        return start_time_str

    @staticmethod
    def print_log(actual_task_name, router_number):
        print("{:<100}".format("-" * 100))
        print("|{:<20} | {:<77}|".format(
            "date",
            datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")))
        print("|{:<20} | {:<77}|".format("actual_task_name", actual_task_name))
        print("|{:<20} | {:<77}|".format("router_number", router_number))