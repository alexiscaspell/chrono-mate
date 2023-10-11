from typing import Dict
from model.calendar import Calendar
from model.issue import Issue,IssueStatus
import random
from model.tasks import Tasks
import datetime

class LoadedHour():
    def __init__(self,spec):
        self.issue = spec.get("issue",None)
        self.hours = spec.get("hours",None)
        self.date = spec.get("date",None)

    def to_dict(self):
        return {        
        "jira ":self.issue.resumen ,
        "prioridad":self.issue.prioridad,
        "status":self.issue.status.value,
        "horas":self.hours,
        "fecha":self.date.date().isoformat(),
        "url":self.issue.url
        }

class HourManager():
    def __init__(self,manager_spec:Dict):
        self.calendar:Calendar = manager_spec["calendar"]
        self.tasks_hours = manager_spec["tasks_hours"]
        self.loaded_issues_w_hours = manager_spec.get("loaded_issues_w_hours",[])
        self.issues = manager_spec.get("issues",[])
        self.hours = manager_spec.get("hours",{})
        tasks = manager_spec["tasks"]
        self.task_lower_hours = int(tasks.lower_hours.split("hs")[0])
        self.task_medium_hours = int(tasks.medium_hours.split("hs")[0])
        self.task_high_hours = int(tasks.high_hours.split("hs")[0])
        self.daily_hours = int(tasks.daily_hours.split("hs")[0])

        total_hours = manager_spec.get("total_hours",str(self.calendar.week_days()*self.daily_hours)+"hs")
        self.total_hours = int(total_hours.split("hs")[0])


    @staticmethod
    def create(hours_spec:Dict,calendar:Calendar,tasks:Tasks):
        tasks_hours = hours_spec.pop(tasks.issues_key,"0%")

        return HourManager({
            "calendar":calendar,
            "tasks_hours":tasks_hours,
            "tasks":tasks,
            "hours": hours_spec
        })

    def load_hour(self,issue:Issue,date:datetime.datetime,hours:int):
        self.loaded_issues_w_hours.append(LoadedHour({
            "issue":issue,
            "hours":hours,
            "date":date
        }))


    def random_task_hours(self,)->int:
        return self.random_hours(self.task_lower_hours,self.task_medium_hours)

    def average_task_hours(self):
        return int((self.task_lower_hours+self.task_medium_hours)/2)

    def high_random_task_hours(self,max_value=None)->int:
        min_value=self.average_task_hours()
        max_value = max_value if max_value and max_value>min_value else  self.task_high_hours

        return self.random_hours(min_value,max_value)

    def random_hours(self,min_value:int,max_value:int)->int:
        return random.randint(min_value,max_value)
    

    def infer_hours(self,hour_str:str)->int:
        return self._infer_hours(hour_str,self.daily_hours)

    def _infer_hours(self,hour_str:str,total_hours:int)->float:
        if hour_str.endswith("%"):
            percentage = float(hour_str.replace("%",""))/100
            return float(total_hours*percentage)
        if hour_str.endswith("hs"):
            return float(hour_str.replace("hs",""))

        raise ValueError(f"{hour_str} no es un valor valido de tiempo")

    def infer_task_hours(self,issue:Issue):
        if issue.status == IssueStatus.TODO:
            return 0
        if issue.status in [IssueStatus.BLOCKED,IssueStatus.DONE]:
            if self.calendar.in_week(issue.fecha_creacion):
                modified_date = issue.fecha_modificacion

                max_hours = int((modified_date-issue.fecha_creacion).days*self.daily_hours)
                max_hours = None if max_hours==0 else max_hours

                return self.high_random_task_hours(max_value=max_hours)/self.calendar.week_days()

            last_comment_in_week = len(issue.comentarios) >0 and self.calendar.in_week(issue.comentarios[-1].fecha)

            if not last_comment_in_week:
                return 0

        return self.random_task_hours()/self.calendar.week_days()

    def valid(self,issue:Issue,date:datetime.datetime)->bool:
        modified_date = issue.fecha_modificacion

        if modified_date<date and issue.status==IssueStatus.DONE:
            return False
        if issue.fecha_creacion>date:
            return False
        if issue.status==IssueStatus.TODO:
            return False

        return True
