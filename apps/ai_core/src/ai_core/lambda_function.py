#!/usr/bin/env python3

import json
import openai
from ai_core.config import settings
from queues.factory import get_queue_client
from ai_core.answer_questions import answer_questions
from datetime import datetime
from ai_core.deepgram_transcription import transcribe, transform

def lambda_handler(event, context):
    print("Received event:", json.dumps(event, indent=2))
    
    # Your logic here (e.g., process queue message)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
