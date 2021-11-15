import os
from typing import List, Optional

import grpc
from fastapi import APIRouter, Query
from vald.v1.payload import payload_pb2
from vald.v1.vald import insert_pb2_grpc, search_pb2_grpc

from src.keywords.keyword_client import KeywordClient
from src.tickets.interface import TicketStatus
from src.tickets.ticket_client import TicketClient
from src.troubles.interface import Trouble, SimilarTroubles, CreatedTrouble, CommentToAdd
from src.vectorizer import vectorize

router = APIRouter()

channel = grpc.insecure_channel(
    f'{os.environ.get("VALD_HOST", "vald-agent-ngt")}:{os.environ.get("VALD_PORT", "8081")}')
insert_stub = insert_pb2_grpc.InsertStub(channel)
insert_config = payload_pb2.Insert.Config(skip_strict_exist_check=True)
search_stub = search_pb2_grpc.SearchStub(channel)
search_config = payload_pb2.Search.Config(num=5, radius=-1.0, epsilon=0.3, timeout=3000000000)


@router.get("/troubles", response_model=List[Trouble])
async def get_troubles(trouble_ids: Optional[List[str]] = Query(None),
                       status: Optional[List[TicketStatus]] = Query(None),
                       free_words: Optional[List[str]] = Query(None),
                       max_results: int = 10) -> List[Trouble]:
    ticket_client = TicketClient()
    tickets = ticket_client.get_ticket_by_jql(trouble_ids, status, free_words, max_results)
    return [Trouble(**ticket.to_dict()) for ticket in tickets]


@router.post("/troubles", response_model=CreatedTrouble)
async def create_trouble(trouble: Trouble) -> CreatedTrouble:
    keyword_client = KeywordClient()
    keywords = keyword_client.get_keywords(trouble.description)

    ticket_client = TicketClient()
    ticket = ticket_client.create_ticket(trouble, keywords)

    return CreatedTrouble(id=ticket.id)


@router.post("/troubles/{trouble_id}/comments")
async def add_comment(trouble_id: str, comment: CommentToAdd):
    ticket_client = TicketClient()
    ticket_client.add_comment(trouble_id, comment.body)


@router.post("/troubles/{trouble_id}/escalate")
async def escalate_trouble(trouble_id: str):
    ticket_client = TicketClient()
    ticket_client.escalate(trouble_id)


@router.post("/troubles/{trouble_id}/back")
async def send_back_trouble(trouble_id: str):
    ticket_client = TicketClient()
    ticket_client.send_back(trouble_id)


@router.post("/troubles/{ticket_id}/vectors")
async def create_vector(ticket_id: str):
    # get trouble description from Jira issues
    ticket_client = TicketClient()
    ticket = ticket_client.get_ticket_by_id(ticket_id)

    # compute vector
    vector = vectorize(ticket.description)  # 768

    # insert to Vald
    request_vector = payload_pb2.Object.Vector(id=ticket_id, vector=vector)
    insert_stub.Insert(payload_pb2.Insert.Request(vector=request_vector, config=insert_config))


@router.get("/troubles/{ticket_id}/similar-troubles", response_model=SimilarTroubles)
async def get_similar_troubles(ticket_id: str) -> SimilarTroubles:
    # get trouble description from Jira issues
    ticket_client = TicketClient()
    ticket = ticket_client.get_ticket_by_id(ticket_id)

    # compute vector
    vector = vectorize(ticket.description)  # 768

    # search in Vald
    res = search_stub.Search(payload_pb2.Search.Request(vector=vector, config=search_config))

    return SimilarTroubles([result.id for result in res.results])
