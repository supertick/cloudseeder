
import logging
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
# FIXME - use pydantic models
# from ai_core.models.transcription_request import Transcription_request
from ai_core.config import settings
import os
from datetime import datetime
import time
import httpx
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Generate a timestamp for the transcript file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

def transform(json_data):
    try:
        logger.info(f"Transforming Deepgram JSON... {json_data}")
        # Open and load the JSON file
        # data = json.load(json_data)
        data = json.loads(json_data)
        
        # Extract the desired data
        input_json = data["results"]["channels"][0]["alternatives"][0]["paragraphs"]["paragraphs"]

        transformed = []
        # Loop through each item in the input JSON
        for item in input_json:
            # Combine all sentence texts into a single string
            combined_text = " ".join(sentence["text"] for sentence in item["sentences"])
            
            # Create the transformed entry
            transformed_entry = {
                "speaker_id": item["speaker"],
                "text": combined_text
            }
            
            # Add the transformed entry to the result list
            transformed.append(transformed_entry)
        
        return transformed
    
    except KeyError as e:
        logger.error(f"Key error: {e}")
    except json.JSONDecodeError:
        logger.error("Invalid JSON format in the input file.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

def transcribe(audio_filename: str):

        # Read the audio file as binary data
        if not os.path.exists(audio_filename):
            raise FileNotFoundError(f"The file {audio_filename} does not exist.")

        with open(audio_filename, "rb") as audio_file:
            buffer_data = audio_file.read()

        return transcribe_buffer(buffer_data)

def transcribe_buffer(buffer_data):
        # Create a Deepgram client using the API key
        deepgram = DeepgramClient(settings.deepgram_api_key)

        payload: FileSource = {
            "buffer": buffer_data,
        }

        # Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            # model="nova-2",
            # smart_format=True,
            # utterances=True,  # Output utterances
            # entities=True,  # Output entities
            # keywords=True,  # Output keywords
            # sentiment=True,  # Output sentiment
            # emotion=True,  # Output emotion
            # intent=True,  # Output intent
            # entities=True,  # Output entities
            diarize=True,  # Enable speaker diarization
            punctuate=True,  # Enable punctuation
            paragraphs=True  # Output formatted paragraphs
        )

        # Call the transcribe_file method with the text payload and options
        response = deepgram.listen.rest.v("1").transcribe_file(payload, options, timeout=httpx.Timeout(300.0, connect=10.0))
        return response.to_json()


if __name__ == "__main__":
    # main()
    data = transform("transcript_1737658924-1737658955.json")
    