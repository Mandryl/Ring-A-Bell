from dataclasses import dataclass
from typing import List, Optional

from pydantic import BaseModel


class Comment(BaseModel):
    author: str
    body: str
    updated: str


class Trouble(BaseModel):
    student_name: str
    summary: str
    description: str
    id: Optional[str] = None
    comments: Optional[List[Comment]] = None
    status: Optional[str] = None


@dataclass
class CommentToAdd:
    body: str


class CreatedTrouble(BaseModel):
    id: str


class SimilarTroubles(BaseModel):
    ticket_ids: List[str]
