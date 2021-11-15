import logging
import os
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

import requests
from fastapi import HTTPException
from requests.auth import HTTPBasicAuth

from src.keywords.interface import Keywords
from src.tickets.interface import Project, IssueType, Assignee, TextContent, Content, Issue, \
    Ticket, CreatedTicket, PlaintextComment, JiraContent, FieldsToCreate, IssueToCreate, CommentToAdd, \
    Transition, TransitionRequest, TicketStatus
from src.troubles.interface import Trouble

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("uvicorn")


@dataclass
class TicketClient:
    project = Project(key=os.environ.get("PROJECT_KEY").strip())
    issue_type = IssueType(id=os.environ.get("ISSUE_TYPE").strip())  # task
    assignee = Assignee(name=os.environ.get("DEFAULT_ASSIGNEE").strip())
    username = os.environ.get("JIRA_USERNAME").strip()
    api_token = os.environ.get("JIRA_API_TOKEN").strip()
    jira_api_url = os.environ.get("JIRA_API_URL").strip()
    jira_browse_url = os.environ.get("JIRA_BROWSE_URL").strip()

    def create_ticket(self, trouble: Trouble, keywords: Keywords) -> CreatedTicket:
        # create new line content
        newline_text_content = TextContent(text="\n")

        # create related tickets title content
        title_text_content = TextContent(text="Related tickets links", marks=[{"type": "strong"}])

        # create related tickets content
        related_tickets = self.get_ticket_by_jql(free_words=[kw.keyword_en for kw in keywords.keyword], max_results=3)
        related_tickets_text = [TextContent(
            text=ticket.summary + "\n",
            marks=[{
                "type": "link",
                "attrs": {
                    "href": f"{self.jira_browse_url}/{ticket.id}"
                }
            }]) for ticket in related_tickets]
        related_content = Content(content=[title_text_content, newline_text_content, *related_tickets_text])

        text_content = TextContent(text=trouble.description)
        content = Content(content=[text_content])
        description = JiraContent(content=[content, related_content])
        fields = FieldsToCreate(
            summary=trouble.summary,
            description=description,
            customfield_10033=trouble.student_name,
            project=self.project,
            issuetype=self.issue_type,
            assignee=self.assignee)
        issue = IssueToCreate(fields=fields)

        res = requests.post(f"{self.jira_api_url}/issue", json=issue.to_dict(),
                            auth=HTTPBasicAuth(self.username, self.api_token))
        if not res.ok:
            raise HTTPException(status_code=res.status_code, detail=res.json())

        try:
            return CreatedTicket(id=res.json()["key"])
        except TypeError:
            raise HTTPException(status_code=500, detail="Unexpected response (without description)")

    def get_ticket_by_id(self, ticket_id: str) -> Ticket:
        params = {"fields": "summary,description,customfield_10033,project,issuetype,assignee,comment,status"}
        res = requests.get(f"{self.jira_api_url}/issue/{ticket_id}",
                           params=params,
                           auth=HTTPBasicAuth(self.username, self.api_token))
        if not res.ok:
            raise HTTPException(status_code=res.status_code, detail=res.json())

        issue = Issue.from_dict(res.json())
        return self._convert_to_ticket(issue)

    def get_ticket_by_jql(self, ticket_ids: Optional[List[str]] = None,
                          status: Optional[List[TicketStatus]] = None,
                          free_words: Optional[List[str]] = None,
                          max_results: int = 10) -> List[Ticket]:
        jql = []
        if ticket_ids is not None:
            jql.append(" OR ".join([f'key="{ticket_id}"' for ticket_id in ticket_ids]))
        if status is not None:
            jql.append(" OR ".join([f'status="{s.value}"' for s in status]))
        if free_words is not None:
            concat_free_words = ' '.join(free_words)
            jql.append(f'text ~ "{concat_free_words}"')
        jql_str = " AND ".join(jql) + " ORDER BY created DESC"

        params = {"jql": jql_str,
                  "maxResults": max_results,
                  "fields": "summary,description,customfield_10033,project,issuetype,assignee,comment,status"}
        res = requests.get(f"{self.jira_api_url}/search",
                           params=params,
                           auth=HTTPBasicAuth(self.username, self.api_token))
        if not res.ok:
            raise HTTPException(status_code=res.status_code, detail=res.json())

        issues = [Issue.from_dict(issue) for issue in res.json()["issues"]]
        return [self._convert_to_ticket(Issue.from_dict(issue)) for issue in issues]

    def add_comment(self, ticket_id: str, comment_body: str):
        comment = CommentToAdd(JiraContent.from_body(comment_body))
        res = requests.post(f"{self.jira_api_url}/issue/{ticket_id}/comment", json=comment.to_dict(),
                            auth=HTTPBasicAuth(self.username, self.api_token))
        if not res.ok:
            raise HTTPException(status_code=res.status_code, detail=res.json())

    def escalate(self, ticket_id: str):
        res = requests.get(f"{self.jira_api_url}/issue/{ticket_id}/transitions",
                           auth=HTTPBasicAuth(self.username, self.api_token))
        if not res.ok:
            raise HTTPException(status_code=res.status_code, detail=res.json())

        transition = Transition(self._get_escalation_transition_id(res.json()["transitions"]))
        res = requests.post(f"{self.jira_api_url}/issue/{ticket_id}/transitions",
                            json=TransitionRequest(transition).to_dict(),
                            auth=HTTPBasicAuth(self.username, self.api_token))
        if not res.ok:
            raise HTTPException(status_code=res.status_code, detail=res.json())

    def send_back(self, ticket_id: str):
        res = requests.get(f"{self.jira_api_url}/issue/{ticket_id}/transitions",
                           auth=HTTPBasicAuth(self.username, self.api_token))
        if not res.ok:
            raise HTTPException(status_code=res.status_code, detail=res.json())

        transition = Transition(self._get_back_transition_id(res.json()["transitions"]))
        res = requests.post(f"{self.jira_api_url}/issue/{ticket_id}/transitions",
                            json=TransitionRequest(transition).to_dict(),
                            auth=HTTPBasicAuth(self.username, self.api_token))
        if not res.ok:
            raise HTTPException(status_code=res.status_code, detail=res.json())

    @staticmethod
    def _convert_to_ticket(issue: Issue):
        try:
            description = issue.fields.description.get_plaintext()
            comments = [PlaintextComment(comment.author.displayName, comment.body.get_plaintext(), comment.updated)
                        for comment in issue.fields.comment.comments]
        except TypeError:
            raise HTTPException(status_code=500, detail="Unexpected response (without description)")

        return Ticket(id=issue.key,
                      student_name=issue.fields.customfield_10033,
                      summary=issue.fields.summary,
                      description=description,
                      comments=comments,
                      status=issue.fields.status.name)

    @staticmethod
    def _get_escalation_transition_id(transitions: List[Dict[Any, Any]]) -> str:
        for transition in transitions:
            if transition["name"] == "escalation":
                return transition["id"]

    @staticmethod
    def _get_back_transition_id(transitions: List[Dict[Any, Any]]) -> str:
        for transition in transitions:
            if transition["name"] == "back":
                return transition["id"]
