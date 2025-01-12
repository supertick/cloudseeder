from fastapi import APIRouter
from ..models.transcription import Transcription

router = APIRouter()

@router.get("/")
def get_all():
    return [{"message": "List of transcriptions"}]

@router.get("/transcription_id")
def get_transcription(transcription_id: int):
    return {"message": "Get a single transcription", "id": transcription_id}

@router.post("/")
def create_transcription(payload: Transcription):
    return {"message": "Create transcription", "data": payload}
