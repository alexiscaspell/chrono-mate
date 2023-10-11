from model.issue import Issue
import utils.jira_util as ju
from typing import List
from utils.excel_util import create_excel_from_list
import argparse
import yaml
from model.configuration import Config
from model.hours import HourManager,LoadedHour
from model.calendar import Calendar
import datetime

WORKBOOK_DIR="files/workbooks"

def load_config_yml(c: str)->Config:

    with open(c) as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    return config

def load_custom_args(config:dict,args:argparse.Namespace):
    if args.today is not None:
        print(f"Reemplazando campo calendar.today con {args.today}")
        config["calendar"]["today"] = args.today

    if args.first_day is not None:
        print(f"Reemplazando campo calendar.first_day con {args.first_day}")
        config["calendar"]["first_day"] = args.first_day

    if args.last_day is not None:
        print(f"Reemplazando campo calendar.last_day con {args.last_day}")
        config["calendar"]["last_day"] = args.last_day

    if args.dry_run is not None:
        dry_run=str(args.dry_run) in ["true","True"]
        print(f"Reemplazando campo dry_run con {dry_run}")
        config["dry_run"] = dry_run

    return config



def main(args:argparse.Namespace):
    config_yml = load_config_yml(args.config)
    config_yml = load_custom_args(config_yml,args)

    config = Config(config_yml)

    ju.connect(jira_user=config.auth.username,jira_pass=config.auth.password)

    issues:List[Issue] = []
    special_issues:List[Issue] = []

    manager:HourManager = config.manager
    calendar:Calendar = config.calendar

    print("OBTENIENDO ISSUES ESPECIALES ...")

    for label in manager.hours:
        special_issues.append(ju.get_issue(config.special_tasks[label]))

    for kanban in config.tasks.kanban_boards:
        print(f"OBTENIENDO ISSUES DE KANBAN {kanban}...")
        issues+=ju.get_user_issues(kanban_board=kanban)

    print("ISSUES OBTENIDAS.")
    
    # issues.sort(key=lambda i:i.issue,reverse=True)

    start =calendar.first_day_week()
    end = calendar.last_day_week()

    week_dates=[]
    delta = datetime.timedelta(days=1)
    while start <= end:
        week_dates.append(start)
        start += delta

    for date in week_dates:
        loaded_hours=0

        print(f"GENERANDO HORAS ESPECIALES FECHA {date.date().isoformat()} ...")

        for special_issue in special_issues:
            if loaded_hours>=manager.daily_hours:
                break

            label = config.get_label(special_issue.issue)
            unrefined_hours = manager.infer_hours(manager.hours[label])

            hours = min(manager.daily_hours-loaded_hours,unrefined_hours)

            if hours>0:
                manager.load_hour(special_issue,date,hours)

            loaded_hours+=hours

        valid_issues = list(filter(lambda i:manager.valid(i,date),issues))

        print(f"GENERANDO HORAS FECHA {date.date().isoformat()} ...")

        for issue_index,issue in enumerate(valid_issues):
            if loaded_hours>=manager.daily_hours:
                break

            unrefined_hours = manager.infer_task_hours(issue)
            hours = min(manager.daily_hours-loaded_hours,unrefined_hours)

            if issue_index==len(valid_issues)-1:
                hours = manager.daily_hours-loaded_hours

            if hours>0:
                manager.load_hour(issue,date,hours)

            loaded_hours+=hours

        print(f"HORAS GENERADAS.")


    if not config.dry_run:
        print(f"CARGANDO HORAS EN JIRA ...")

        for lh in manager.loaded_issues_w_hours:
            ju.log_hours_by_date(lh.issue,lh.date,lh.date,lh.hours*60*60)

        print(f"HORAS EN JIRA CARGADAS.")

    excel_file = f"{WORKBOOK_DIR}/workbook_{calendar.today.date().isoformat()}.xlsx"

    print(f"CARGANDO DATOS EN EXCEL ...")

    create_excel_from_list([lh.to_dict() for lh in manager.loaded_issues_w_hours],excel_file)

    print(f"DATOS CARGADOS EN {excel_file} .")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="chrono-mate")
    parser.add_argument('config', default='files/config.yml',
                        help='Configuration file to use')
    parser.add_argument('--today', default=None,
                        help='Date of today in YYYY-MM-DD format')
    parser.add_argument('--first_day', default=None,
                        help='Name of first day of the week (ex. lunes)')
    parser.add_argument('--last_day', default=None,
                        help='Name of last day of the week (ex. viernes)')
    parser.add_argument('--dry_run', default=None,
                        help='Dry run mode activated')

    main(parser.parse_args())
