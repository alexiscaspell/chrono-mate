from typing import Dict

class Tasks():
    def __init__(self,spec:Dict):
        self.kanban_boards = spec.get("kanban_boards",[])
        self.issues_key = spec["issues_key"]
        self.lower_hours = spec["lower_hours"]
        self.medium_hours = spec["medium_hours"]
        self.high_hours = spec["high_hours"]
        self.daily_hours = spec.get("daily_hours","8hs")
