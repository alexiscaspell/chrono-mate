from utils.date_util import cast_to_datetime,now_iso8601_utc,to_utc,between
from typing import Dict
import datetime
from enum import Enum

class Day(Enum):
    lunes = 0
    martes = 1
    miercoles = 2
    jueves = 3
    viernes = 4

    @staticmethod
    def from_str(label):
        return Day[label]

class Calendar():
    def __init__(self,spec:Dict):
        today = spec["today"] if spec.get("today",None) else None

        if today:
            today = today if today and "T" in today and ":" in today else today+"T00:00:00Z"

        self.today = to_utc(cast_to_datetime(today) if today else now_iso8601_utc(3),3)

        self.first_day = Day.from_str(spec.get("first_day","lunes"))
        self.last_day =  Day.from_str(spec.get("last_day","viernes"))
        
    def first_day_week(self)->datetime.datetime:
        return self.today - datetime.timedelta(days=self.today.weekday())+datetime.timedelta(days=self.first_day.value)

    def last_day_week(self)->datetime.datetime:
        if self.first_day==self.last_day:
            return self.first_day_week()
            
        days_diff = self.week_days()
        return self.first_day_week() + datetime.timedelta(days=days_diff)

    def in_week(self,some_date:datetime.datetime)->bool:
        return between(some_date,self.first_day_week(),self.last_day_week())

    def week_days(self)->int:
        return max(self.last_day.value-self.first_day.value,1)