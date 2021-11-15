import dataclasses
import enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from dataclasses_json import dataclass_json


@dataclass
class Project:
    key: str


@dataclass
class IssueType:
    id: str


@dataclass
class Assignee:
    name: str


@dataclass
class TextContent:
    text: str
    type: str = "text"
    marks: List[Dict[str, Any]] = dataclasses.field(default_factory=list)


@dataclass
class Content:
    content: List[TextContent]
    type: str = "paragraph"


@dataclass
class JiraContent:
    content: List[Content]
    type: str = "doc"
    version: int = 1

    def get_plaintext(self):
        return self.content[0].content[0].text

    @staticmethod
    def from_body(body: str):
        text_content = TextContent(body)
        content = Content([text_content])
        return JiraContent([content])


@dataclass
class Visibility:
    type: str = "role"
    value: str = "Administrators"


@dataclass
class FieldsToCreate:
    summary: str
    description: JiraContent
    customfield_10033: str  # student name
    project: Project
    issuetype: IssueType
    assignee: Assignee


@dataclass_json
@dataclass
class IssueToCreate:
    fields: FieldsToCreate
    key: str = ""


@dataclass
class Author:
    accountId: str
    displayName: str


@dataclass
class Comment:
    author: Author
    body: JiraContent
    updated: str


@dataclass
class Comments:
    comments: List[Comment]


@dataclass_json
@dataclass
class CommentToAdd:
    body: JiraContent
    visibility: Visibility = Visibility()


@dataclass
class Status:
    name: str


@dataclass
class Fields:
    summary: str
    description: JiraContent
    customfield_10033: str  # student name
    project: Project
    issuetype: IssueType
    assignee: Assignee
    status: Status
    comment: Optional[Comments] = None


@dataclass_json
@dataclass
class Issue:
    fields: Fields
    key: str = ""


@dataclass
class PlaintextComment:
    author: str
    body: str
    updated: str


@dataclass_json
@dataclass
class Ticket:
    id: str
    student_name: str
    summary: str
    description: str
    status: str
    comments: Optional[List[PlaintextComment]] = None


@dataclass_json
@dataclass
class CreatedTicket:
    id: str


class TicketStatus(enum.Enum):
    OPEN = "Open"
    CLASS_TEACHER = "Class Teacher Review"
    VICE_PRINCIPAL = "Vice Principal Review"
    BOARD_OF_EDUCATION = "Board of Education Review"
    RESOLVED = "Resolved"


@dataclass
class Transition:
    id: str


@dataclass_json
@dataclass
class TransitionRequest:
    transition: Transition
