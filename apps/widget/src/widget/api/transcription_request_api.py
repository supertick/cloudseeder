from fastapi import APIRouter
from ..models.transcription_request import Transcription_request

router = APIRouter()

@router.get("/")
def get_all():
    return [{"message": "List of transcription_requests"}]

@router.get("/transcription_request_id")
def get_transcription_request(transcription_request_id: int):
    return {"message": "Get a single transcription_request", "id": transcription_request_id}

@router.post("/")
def create_transcription_request(payload: Transcription_request):
    return {"message": "Create transcription_request", "data": payload}
