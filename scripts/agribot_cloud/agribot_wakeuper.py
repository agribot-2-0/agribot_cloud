class AgribotWakeuper:
    task_keys = [
        "wind_value", "wind_condition", "temperature_value",
        "temperature_condition", "pressure_value", "pressure_condition",
        "humidity_value", "humidity_condition", "start_time"
    ]

    def __init__(self, firestore, sms_api):
        self.firestore = firestore
        self.sms_api = sms_api

    def run(self):
        self.firestore.listen_on_actual_task_change(
            self.agribot_program_function)

    # http://stackoverflow.com/q/3844948/
    # Check if list is empty
    @staticmethod
    def check_equal_ivo(lst):
        return not lst or lst.count(lst[0]) == len(lst)

    def agribot_program_function(self, agribot_number, condtions_dict):
        message_body = []

        for key in self.task_keys:
            if key in condtions_dict:
                if key == "start_time":
                    message_body.append(
                        str(condtions_dict[key].strftime("%Y-%m-%d-%H:%M")))
                else:
                    message_body.append(str(condtions_dict[key]))
            else:
                print("|{:<100}|".format(
                    "SMS not send. Task definition is incomplete."))
                return

        if self.check_equal_ivo(message_body):
            message_body = "startnow"
        else:
            message_body = '#'.join(message_body)
            message_body = 'config ' + message_body
        self.sms_api.send_sms(agribot_number, message_body)
