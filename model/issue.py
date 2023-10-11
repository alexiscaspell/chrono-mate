import json
from model.comment import Comment
from enum import Enum
from utils.date_util import cast_to_datetime,to_utc
from jira import Issue as JiraIssue

class IssueStatus(Enum):
    TODO = "To Do"
    INPROGRESS = "In Progress"
    BLOCKED = "Blocked"
    TESTING = "Testing"
    DONE = "Done"

    @staticmethod
    def from_str(label):
        label_lwc = label.lower()

        in_progress_list=["in progress","in development",
        "in analysis","developed","in approval",
        "ready to develop","ready to deploy",""]

        if label_lwc=="to do":
            return IssueStatus.TODO
        elif label_lwc in in_progress_list:
            return IssueStatus.INPROGRESS
        elif label_lwc in ["blocked","bloqueado"]:
            return IssueStatus.BLOCKED
        elif label_lwc in ["in testing","testing"]:
            return IssueStatus.TESTING
        elif label_lwc in ["done","cancelled","installed"]:
            return IssueStatus.DONE
        else:
            raise NotImplementedError(f"No existe conversion para {label}")



class IssueStatusChange():
    def __init__(self,spec:dict):
        self.fecha = spec["fecha"]
        self.from_status = spec["from_status"]
        self.to_status = spec["to_status"]

    @staticmethod
    def from_history_item(item,history)->"IssueStatusChange":
        return IssueStatusChange({
            "fecha":to_utc(cast_to_datetime(history.created),3),
            "from_status":IssueStatus.from_str(item.fromString),
            "to_status":IssueStatus.from_str(item.toString)
        })

class StatusChangeLog():
    def __init__(self,spec:dict):
        self.cambios = spec.get("cambios",[])
        self.cambios.sort(key=lambda c:c.fecha,reverse=False)

    @staticmethod
    def from_change_log(changelog)->"StatusChangeLog":
        status_changes=[]
        for history in changelog.histories:
            for item in history.items:
                if item.field == 'status':
                    status_changes.append(IssueStatusChange.from_history_item(item,history))
                    
        return StatusChangeLog({
            "cambios":status_changes
        })

    def last_change(self)->IssueStatusChange:
        return self.cambios[-1] if len(self.cambios)>0 else None

class Issue():
    def __init__(self, spec: dict):
        self.id = spec.get("id",None)
        self.issue = spec["issue"]
        self.url = spec["url"]
        self.usuario = spec.get("usuario",None)
        self.prioridad = spec.get("prioridad",None)
        self.tipo = spec.get("tipo",None)
        self.status = spec.get("status",None)
        self.etiquetas = spec.get("etiquetas",None)
        self.resumen = spec.get("resumen",None)
        self.status_changelog = spec["status_changelog"]

        fecha_modificacion=spec.get("fecha_modificacion",None)
        if self.status_changelog.last_change():
            fecha_modificacion=self.status_changelog.last_change().fecha

        self.fecha_modificacion =  fecha_modificacion

        self.fecha_creacion = spec.get("fecha_creacion",None)
        self.comentarios = spec.get("comentarios",[])

    def infer_issue_url(issue, jira_api_url):
        return f"{jira_api_url}/browse/{issue}"

    def from_jira_issue(jira_issue:JiraIssue, jira_api_url):
        return Issue({
            "issue": jira_issue.key,
            "id":jira_issue.id,
            "url": Issue.infer_issue_url(jira_issue,jira_api_url),
            "status_changelog": StatusChangeLog.from_change_log(jira_issue.changelog),
            "usuario": jira_issue.fields.assignee.displayName if jira_issue.fields.assignee else "Unasigned",
            "prioridad": jira_issue.fields.priority.name if hasattr(jira_issue.fields,"priority") else None,
            "tipo": jira_issue.fields.issuetype.name,
            "status": IssueStatus.from_str(jira_issue.fields.status.statusCategory.name),
            "etiquetas": jira_issue.fields.labels if hasattr(jira_issue.fields,"labels") else [],
            "resumen": jira_issue.fields.summary,
            "fecha_creacion":cast_to_datetime(jira_issue.fields.created),
            "fecha_modificacion":cast_to_datetime(jira_issue.fields.updated),
            "tiempo_estimado":jira_issue.fields.timeestimate,
            "comentarios": [Comment.from_jira_comment(c) for c in jira_issue.fields.comment.comments ]
        })

    def __repr__(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            "issue": self.issue,
            "url": self.url,
            "usuario": self.usuario,
            "prioridad": self.prioridad,
            "tipo": self.tipo,
            "status": self.status,
            "etiquetas": self.etiquetas,
            "resumen": self.resumen,
            "fecha_creacion":self.fecha_creacion,
            "fecha_modificacion":self.fecha_modificacion
        }
