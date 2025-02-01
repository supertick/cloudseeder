from queues.interface import QueueClient
from ai_core.models.transcription_request import Transcription_request, Transcription_request
from database.interface import NoSqlDb

def create_transcription_request(item: Transcription_request, db: NoSqlDb, q: QueueClient, user: dict):
    print("===============Transcription request service called==============")
    print(item)