from utils.date_util import cast_to_datetime

class Comment():
    def __init__(self,spec:dict):
        self.usuario = spec["usuario"]
        self.mensaje = spec["mensaje"]
        self.fecha = spec["fecha"]

    def from_jira_comment(jira_comment):
        return Comment({
            "usuario":jira_comment.updateAuthor.displayName,
            "mensaje": jira_comment.body,
            "fecha":cast_to_datetime(jira_comment.updated)
        })