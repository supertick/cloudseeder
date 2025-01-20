from deepgram import DeepgramClient, PrerecordedOptions, FileSource
import os
from datetime import datetime
import time
import httpx

# DG_KEY = os.getenv('DEEPGRAM_API_KEY')
# if not DG_KEY:
#     raise ValueError("DEEPGRAM_API_KEY environment variable is not set.")

DG_KEY = "4e6eca2f128d1261c9aabd8ee0a7b503861d0ce1"

# Local audio file path
# AUDIO_SOURCE = "tests/test_data/audio_1733445520112.wav"
AUDIO_SOURCE = "tests/test_data/kate.webm"

# Generate a timestamp for the transcript file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")


def main():
    try:
        # STEP 1: Create a Deepgram client using the API key
        deepgram = DeepgramClient(DG_KEY)

        start_time = int(time.time())

        # STEP 2: Read the audio file as binary data
        if not os.path.exists(AUDIO_SOURCE):
            raise FileNotFoundError(f"The file {AUDIO_SOURCE} does not exist.")

        with open(AUDIO_SOURCE, "rb") as audio_file:
            buffer_data = audio_file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        PrerecordedOptions()

        # STEP 3: Configure Deepgram options for audio analysis
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

        # STEP 4: Call the transcribe_file method with the text payload and options
        # response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)

        # response = deepgram.transcription.prerecorded.transcribe_file(payload, options)

        response = deepgram.listen.rest.v("1").transcribe_file(payload, options, timeout=httpx.Timeout(300.0, connect=10.0))

        TRANSCRIPT_FILE = f"transcript_{start_time}-{int(time.time())}.json"
        # STEP 5: Write the response JSON to a timestamped file
        with open(TRANSCRIPT_FILE, "w") as transcript_file:
            transcript_file.write(response.to_json(indent=4))

        print(f"Transcript JSON file generated successfully: {TRANSCRIPT_FILE}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    main()