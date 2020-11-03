import datetime
import time
import threading


class AgribotScheduler:
    # pylint: disable=too-many-instance-attributes
    def __init__(self, agribot_firestore, weather_forecast, event, logger):
        self.logger = logger
        self.callback_done = event
        self.weather_forecast = weather_forecast
        self.agribot_firestore = agribot_firestore
        self.tasks_highest = ""

        self.check_highest_task_time_loop = threading.Thread(
            target=self.check_highest_task_time, args=[60])
        self.request_forecast_data_loop = threading.Thread(
            target=self.request_forecast_data, args=[3600])

        self.check_highest_task_time_loop.daemon = True
        self.request_forecast_data_loop.daemon = True
        self.robot_rsn = ""

    def check_highest_task_time(self, sleep_time):
        while True:
            if self.tasks_highest:
                task_name = self.agribot_firestore.get_task(
                    self.robot_rsn, self.tasks_highest)
                if task_name.to_dict():
                    start_time = task_name.to_dict()["start_time"]
                    self.logger.info(
                        "Highest task is {} with start time {}, actual time is {}"
                        .format(self.tasks_highest, start_time,
                                self.get_time_now()))
                    if self.get_time_now(offset_hours=-1) > start_time:
                        self.agribot_firestore.update_actual_task(
                            self.robot_rsn, self.tasks_highest)
            time.sleep(sleep_time - time.time() % sleep_time)

    def request_forecast_data(self, sleep_time):
        while True:
            self.logger.info("Request forecast")
            self.weather_forecast.request_one_day_hourly_forecast_data()
            time.sleep(sleep_time - time.time() % sleep_time)

    def run(self, robot_rsn):
        self.robot_rsn = robot_rsn
        self.register_callbacks(robot_rsn)
        self.check_highest_task_time_loop.start()
        self.request_forecast_data_loop.start()

    def register_callbacks(self, agribot_rsn):
        self.agribot_firestore.register_on_tasks_change_callback(
            agribot_rsn, self.on_tasks_change_callback)
        self.agribot_firestore.register_on_robot_change_callback(
            agribot_rsn, self.on_robot_change_callback)

    def on_tasks_change_callback(self, doc_snapshot, changes, read_time):  # pylint: disable=unused-argument,no-self-use
        # Estimate time for weather tasks
        for change in changes:
            if change.type.name == 'ADDED' or change.type.name == "MODIFIED":
                self.update_estimated_time(self.robot_rsn, change.document)

        # Update tasks ordered field
        self.update_tasks_order()

        self.callback_done.set()

    def on_robot_change_callback(self, doc_snapshot, changes, read_time):  # pylint: disable=unused-argument,no-self-use
        self.logger.info("Scheduler robot change")
        actual_task_name = doc_snapshot[0].to_dict()['actual_task']
        tasks_ordered = doc_snapshot[0].to_dict()['tasks_ordered']

        # Set first task in tasks_ordered as actual_task
        if tasks_ordered:
            if actual_task_name == "":
                self.logger.info("New actual task")
                self.tasks_highest = tasks_ordered[0]
        else:
            self.tasks_highest = ""

        self.logger.info("actual_task_name is {}".format(actual_task_name))
        self.callback_done.set()

    def update_tasks_order(self):
        tasks = self.agribot_firestore.get_tasks_stream(self.robot_rsn,
                                                        order_by="start_time")
        self.agribot_firestore.update_tasks_ordered(self.robot_rsn, tasks)

    def update_estimated_time(self, robot_rsn, task_document):
        if task_document.to_dict()['start_time_estimated'] is True:
            estimated_time = self.estimate_start_time(task_document)
            if estimated_time is not None:
                self.agribot_firestore.update_start_time(
                    robot_rsn, task_document.id, estimated_time)
                self.logger.info("Task {} estimated time is {}".format(
                    task_document.id, estimated_time))

    def estimate_start_time(self, task_document):
        weather_parameters = {
            "temperature": self.weather_forecast.get_forecast_temperature(),
            "humidity": self.weather_forecast.get_forecast_humidity(),
            "wind": self.weather_forecast.get_forecast_wind_speed()
        }
        weather_forecasts = []
        estimated_time = None

        for firebase_param, weather_forecast_function in weather_parameters.items(
        ):
            value_key = "{}_{}".format(firebase_param, "value")
            cond_key = "{}_{}".format(firebase_param, "condition")

            value = task_document.to_dict()[value_key]
            cond = task_document.to_dict()[cond_key]

            if value != "*" and cond != "*":
                forecast_filtered = self.weather_forecast.if_weather_condition_fullfiled(
                    weather_forecast_function, cond, value)
                if bool(forecast_filtered):
                    weather_forecasts.append(list(forecast_filtered.keys()))

        if weather_forecasts:
            elements_in_all = list(
                set.intersection(*map(set, weather_forecasts)))
        else:
            elements_in_all = []

        if elements_in_all:
            elements_in_all.sort()
            estimated_time = elements_in_all[0]
        else:
            # reshedule for next 24 hours
            estimated_time = self.get_time_now(offset_hours=24)

        return estimated_time

    def delete_tasks(self, agribot_rsn, tasks):
        for task_name in tasks:
            self.agribot_firestore.delete_task(agribot_rsn, task_name.id)

    @staticmethod
    def get_time_now(offset_hours=0, offset_minutes=0):
        return datetime.datetime.now(datetime.timezone.utc).replace(
            second=0, microsecond=0) + datetime.timedelta(
                hours=offset_hours, minutes=offset_minutes)

    def print_tasks(self, tasks):
        self.logger.info("{:<100}".format("tasks"))
        for task_name in tasks:
            self.logger.info("{} | {} | {}".format(
                task_name.id,
                task_name.to_dict()["start_time"].strftime("%Y-%m-%d %H:%M"),
                task_name.to_dict()["start_time_estimated"]))
