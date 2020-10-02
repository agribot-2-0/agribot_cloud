import datetime
import time
import threading


class AgribotScheduler:
    def __init__(self, agribot_firestore, event, logger):
        self.logger = logger
        self.callback_done = event
        self.agribot_firestore = agribot_firestore
        self.tasks_highest = ""
        self.loop_thread = threading.Thread(
            target=self.check_highest_task_time)
        self.loop_thread.daemon = True  # stop if the program exits

    def check_highest_task_time(self):
        while True:
            self.logger.info("{:<100}".format("-" * 80))
            self.logger.info("check_highest_time")
            self.logger.info(self.tasks_highest)
            robot_rsn = "ADI75R1"
            time_now = datetime.datetime.now(datetime.timezone.utc)
            if self.tasks_highest:
                task = self.agribot_firestore.get_task(robot_rsn,
                                                       self.tasks_highest)
                start_time = task.to_dict()["start_time"]
                self.logger.info(start_time)
                self.logger.info(time_now)
                if time_now > start_time:
                    self.agribot_firestore.update_actual_task(
                        robot_rsn, self.tasks_highest)
            time.sleep(10)

    def run(self):
        self.register_callbacks("ADI75R1")
        self.loop_thread.start()

    def register_callbacks(self, agribot_rsn):
        self.agribot_firestore.register_on_tasks_change_callback(
            agribot_rsn, self.on_tasks_change_callback)
        self.agribot_firestore.register_on_robot_change_callback(
            agribot_rsn, self.on_robot_change_callback)

    def on_tasks_change_callback(self, doc_snapshot, changes, read_time):  # pylint: disable=unused-argument,no-self-use
        self.logger.info("{:<100}".format("-" * 80))
        self.logger.info("Scheduler tasks change")
        # update tasks ordered field
        tasks = self.agribot_firestore.get_tasks_stream("ADI75R1",
                                                        order_by="start_time")
        self.agribot_firestore.update_tasks_ordered("ADI75R1", tasks)

        # print tasks
        tasks = self.agribot_firestore.get_tasks_stream("ADI75R1",
                                                        order_by="start_time")
        self.print_tasks(tasks)

        self.callback_done.set()

    def on_robot_change_callback(self, doc_snapshot, changes, read_time):  # pylint: disable=unused-argument,no-self-use
        self.logger.info("{:<100}".format("-" * 80))
        self.logger.info("Scheduler robot change")
        robot_rsn = doc_snapshot[0].id
        actual_task_name = self.agribot_firestore.get_actual_task(robot_rsn)
        tasks_ordered = self.agribot_firestore.get_tasks_ordered(robot_rsn)

        # Set first task in tasks_ordered as actual_task
        if tasks_ordered:
            if actual_task_name == "":
                self.logger.info(datetime.datetime.now())
                self.logger.info("New task")
                self.tasks_highest = tasks_ordered[0]
            else:
                self.tasks_highest = ""

        # if actual_task_name == "":
        #     print("Task is empty")
        #     self.agribot_firestore.delete_task(robot_rsn, self.tasks_highest)
        self.logger.info("actual_task_name {}".format(actual_task_name))
        self.callback_done.set()

    def delete_tasks(self, agribot_rsn, tasks):
        for task in tasks:
            self.agribot_firestore.delete_task(agribot_rsn, task.id)

    def print_tasks(self, tasks):
        self.logger.info("{:<100}".format("tasks"))
        for task in tasks:
            self.logger.info("{} | {}".format(
                task.id,
                task.to_dict()["start_time"].strftime("%Y-%m-%d %H:%M")))
