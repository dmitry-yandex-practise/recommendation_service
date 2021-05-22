import json
from datetime import date
from uuid import uuid4

from fastapi import APIRouter, Depends
from event_services.event import get_event_service, EventService
from event_models.event import BaseEvent, ReviewEvent
from api.v1.models import EventResp

router = APIRouter()


@router.post('/send_event/', response_model=EventResp)
async def event(event: BaseEvent, event_service: EventService = Depends(get_event_service)) -> EventResp:
    result = await event_service.send_event(event.topic, event.key, event.value)
    response = EventResp(success=result)
    return response

@router.post('/send_review_event/', response_model=EventResp)
async def event(event: ReviewEvent, event_service: EventService = Depends(get_event_service)) -> EventResp:
    review_event_key = str(uuid4())
    json_data = json.dumps({"film_work_id": str(event.movie_id),
                            "user_id": str(event.user_id),
                            "score": str(event.score),
                            "reviw_date": date.today().strftime("%Y-%m-%d")})
    result = await event_service.send_event(event.topic, review_event_key, json_data)
    response = EventResp(success=result)
    return response
