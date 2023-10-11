from typing import Dict
from model.calendar import Calendar
from model.hours import HourManager
from model.tasks import Tasks

class Auth():
    def __init__(self,spec:Dict):
        self.username = spec["username"]
        self.password = spec["password"]

class Config():
    def __init__(self,spec:Dict):
        self.auth = Auth(spec["auth"])
        self.special_tasks = spec.get("special_tasks",{})
        self.calendar = Calendar(spec["calendar"])
        self.tasks = Tasks(spec["tasks"])
        self.hours = spec["hours"]
        self.manager = HourManager.create(spec["hours"],self.calendar,self.tasks)
        self.dry_run = spec.get("dry_run",False)

    def get_label(self,issue_name):
        inv_map = {v: k for k, v in self.special_tasks.items()}
        return inv_map[issue_name] if issue_name in inv_map else None