from fastapi import APIRouter
from ..models.transcription_result import Transcription_result

router = APIRouter()

@router.get("/")
def get_all():
    return [{"message": "List of transcription_results"}]

@router.get("/transcription_result_id")
def get_transcription_result(transcription_result_id: int):
    return {"message": "Get a single transcription_result", "id": transcription_result_id}

@router.post("/")
def create_transcription_result(payload: Transcription_result):
    return {"message": "Create transcription_result", "data": payload}
