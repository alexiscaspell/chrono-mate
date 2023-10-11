from jira import JIRA,Worklog
from model.issue import Issue
import os
import datetime
from typing import Union,Optional,Dict,Any,List
import json

JIRA_USER = os.getenv("JIRA_USER",None)
JIRA_PASS = os.getenv("JIRA_PASS",None)
JIRA_API_URL = os.getenv("JIRA_URL","https://jira.prismamp.com")
JIRA_API_TIMEOUT = int(os.getenv("JIRA_TIMEOUT",10000))
MOCK_JIRA_ON_FAIL = os.getenv("JIRA_MOCK_ON_FAIL","false")=="true"
MOCK_JIRA = os.getenv("JIRA_MOCK","false")=="true"

jira_client = None
jira_username=None


def connect(jira_user=None,jira_pass=None):
    global jira_client
    global jira_username

    jira_user = JIRA_USER if not jira_user else jira_user
    jira_pass = JIRA_PASS if not jira_pass else jira_pass

    if jira_client is None:
        jira_username= jira_user

        options = {
            'server': JIRA_API_URL
        }
        jira_client = JIRA(options, basic_auth=(jira_user, jira_pass),timeout=JIRA_API_TIMEOUT)

    return jira_client


def get_user_issues(username=None,kanban_board=None):
    username = "currentUser()" if not username else username

    jira_client = connect()

    search_query = f'assignee = {username}'

    if kanban_board:
        search_query+=f' AND project="{kanban_board}"'

    issues = jira_client.search_issues(search_query,maxResults=False,expand='changelog')

    return [Issue.from_jira_issue(i,JIRA_API_URL) for i in issues]


def get_issue(issue_name:str)->Issue:
    if MOCK_JIRA:
        print("Mockeando issue ...")
        return Issue({"issue":issue_name,"url":Issue.infer_issue_url(issue_name,JIRA_API_URL)})

    try:
        jira_client = connect()

        issue = jira_client.issue(issue_name,expand='changelog')
        
        return Issue.from_jira_issue(issue,JIRA_API_URL)
    except Exception as e:
        print(f"Error al obtener issue {issue_name} de jira")

        if not MOCK_JIRA_ON_FAIL:
            raise e
        
        print("Mockeando issue ...")

        return Issue({"issue":issue_name,"url":Issue.infer_issue_url(issue_name,JIRA_API_URL)})




def log_hours_by_date(issue:Issue,start_date:datetime.datetime,end_date:datetime.datetime,average_time_per_day_seconds:float)->List[Worklog]:
    worklogs=[]

    number_of_days_worked = (end_date - start_date).days + 1
    average_hours = average_time_per_day_seconds/(60*60)

    for day in range(number_of_days_worked):
        worklog = _log_hours(issue=issue,hours=average_hours,start_date=start_date+datetime.timedelta(days=day))
        worklogs.append(worklog)

    return worklogs

def _log_hours(issue:Issue,hours:int,start_date:datetime.datetime=None)->Worklog:
    jira_client = connect()
    
    return jira_client.add_worklog(issue=issue.issue,timeSpent='{}h'.format(hours),started=start_date)


def log_hours(issue:Issue,hours:int)->Worklog:
    return _log_hours(issue=issue,hours=hours)