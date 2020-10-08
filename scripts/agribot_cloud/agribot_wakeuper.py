class AgribotWakeuper:
    task_keys = [
        "wind_value", "wind_condition", "temperature_value",
        "temperature_condition", "pressure_value", "pressure_condition",
        "humidity_value", "humidity_condition", "start_time"
    ]

    null_program_character = '*'
    start_now_time = "2000-01-01-12:00"

    def __init__(self, firestore, sms_api, event, logger):
        self.logger = logger
        self.callback_done = event
        self.agribot_firestore = firestore
        self.sms_api = sms_api
        self.actual_task_listeners = {}
        self.robot_rsn = ""

    def run(self, robot_rsn):
        self.robot_rsn = robot_rsn
        self.agribot_firestore.register_on_robot_change_callback(
            robot_rsn, self.actual_task_callback)

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
                self.logger.info("{:<100}".format(
                    "SMS not send. Task definition is incomplete."))
                return

        if self.check_equal_elements(message_body):
            message_body = "startnow"
        else:
            message_body = '#'.join(message_body)
            message_body = 'config ' + message_body
        self.sms_api.send_sms(agribot_number, message_body)

    def actual_task_callback(self, doc_snapshot, changes, read_time):  # pylint: disable=unused-argument,no-self-use
        self.logger.info("Wakeuper robot change")
        actual_task_name = self.agribot_firestore.get_actual_task(
            self.robot_rsn)
        if actual_task_name:
            router_number = self.agribot_firestore.get_router_number(
                self.robot_rsn)
            tasks_ref = self.agribot_firestore.get_tasks_stream(self.robot_rsn)
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

    def print_log(self, actual_task_name, router_number):
        self.logger.info("Actual task is {}, send it to {}".format(
            actual_task_name, router_number))
