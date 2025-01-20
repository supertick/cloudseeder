import json
import boto3
import os
import time
import tempfile
import logging

from typing import List

from slack_sdk import WebClient

from pydub import AudioSegment

# Create logger object
logger = logging.getLogger()

# Get Environment Varibales
slack_channel_name = os.environ.get("SLACK_CHANNEL_NAME")
secret_store = os.environ.get("SECRET_STORE_NAME")
testing_flag = os.environ.get("TESTING_FLAG")

# Create a s3 client
s3_client = boto3.client('s3')
secret_client = boto3.client('secretsmanager')
transcribe_client = boto3.client('transcribe')

bucket_name = "dev-acutedge-recordings"
s3_base_uri = "https://dev-acutedge-recordings.s3.amazonaws.com/"

# Set the FFMPEG_BINARY environment variable
os.environ["FFMPEG_BINARY"] = "ffmpeg/ffmpeg"
os.environ["PATH"] = "ffmpeg"

# ---------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------
    
# Function to extract timestamp from filename
def extract_timestamp(filename):
    return int(filename.split('_')[1].split('.')[0])

# Sorted object key list for chunks
def get_sorted_object_key_for_merging(object_key_list: List) -> List:
    """
    Get sorted object keys using timestamp placed in filename
    """
    return sorted(object_key_list, key=extract_timestamp)

# Send messages to Slack Channel
def send_message_to_slack_channel(slack_client, channel_name: str, message: str):
    """
    Send a message to Slack Channel using Bot User
    """
    try:
        slack_client.chat_postMessage(
            channel=channel_name,
            text=message
        )
    except Exception as e:
        print(f"ERROR : {str(e)} & Line No.- {e.__traceback__.tb_lineno}")


# ---------------------------------------------------------------------
# Functions for communicating with aws s3
# ---------------------------------------------------------------------

def get_s3_object_content(object_key):
    """
    Retrieve an object content from an S3 bucket using its key
    """
    print("object_key : ", object_key)
    obj = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    return obj['Body'].read()
    
def upload_s3_object(file_content, key):
    """
    Upload an object to S3 bucket using its key
    """
    s3_client.upload_fileobj(file_content, Bucket=bucket_name, Key=key)
    
def list_s3_folder_contents(folder_name) -> List[str]:
    """
    List all objects in a specified folder within an S3 bucket.
    
    :param folder_name: The name of the folder (prefix) within the S3 bucket.
    :return: A list of object keys in the specified folder.
    """
    paginator = s3_client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=folder_name)

    object_keys = []
    for page in page_iterator:
        if 'Contents' in page:
            for obj in page['Contents']:
                object_keys.append(obj['Key'])

    return object_keys

def generate_s3_pre_signed_url(object_key, expiry: int = 3600) -> str:
    """
    Generates pre signed url for an object
    """
    return s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': object_key}, ExpiresIn=expiry)


# ---------------------------------------------------------------------
# SECRET MANAGER
# ---------------------------------------------------------------------
def get_secret_by_name(secret_key_name: str):
    """
    Retrieve an object content from an S3 bucket using its key
    """
    try:
        response = secret_client.get_secret_value(SecretId=secret_store)
        secrets_dict = json.loads(response['SecretString'])
        
        if secrets_dict:
            return secrets_dict.get(secret_key_name)
            
    except Exception as e:
        raise e
    

# ---------------------------------------------------------------------
# Functions for merging chunks and create a signlle audio file
# ---------------------------------------------------------------------

def create_combined_audio_from_chunks(sorted_objects_key_list: List) -> AudioSegment:
    """
    Create a merged audio from audio chunks
    """
    
    # Create an empty AudioSegment object to hold the combined audio
    combined_audio = AudioSegment.empty()
    
    # Create a single file from audio chunks
    for key in sorted_objects_key_list:
        try:
            file_content = get_s3_object_content(object_key=key)
    
            # Create a temporary file and write the object content to it
            with tempfile.NamedTemporaryFile(delete=True) as temp_file:
                temp_file.write(file_content)
                temp_file.seek(0)
    
                sound = AudioSegment.from_file_using_temporary_files(temp_file)
    
            combined_audio += sound
            
        except Exception as e:
            error_message = f"ERROR : {str(e)} and Line no. : {e.__traceback__.tb_lineno}"
            error_dict = {
                "message": error_message,
                "description": f"error has been raised while getting chunk and creating merged audio file and error raised while processign key : {key}"
            }
            logger.error(error_dict)
    
    return combined_audio
    
def create_single_audio_file_and_save_to_s3(slack_client, combined_audio: AudioSegment, single_recording_object_folder_path, patient_id: str, encounter_id: str, assessment_id: str)-> bool:
    """
    Creates a single audio file and store it to single named folder path of s3
    """
    try:
        # METHOD -1 : Using Temp Files
        # Export the combined audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=True) as temp_output_file:
            output_file_path = temp_output_file.name
            combined_audio.export(output_file_path, format="wav")
            
            # Store to s3
            output_file_key = single_recording_object_folder_path + "audio_file.wav"
            upload_s3_object(file_content=temp_output_file, key=output_file_key)
            logger.info("Merged audio file uploaded successfully to single named folder of s3.")

            job_name = f"transcribe_{patient_id}_{encounter_id}"
            file_uri = f's3://{bucket_name}/{output_file_key}'
            response = start_transcription_job(slack_client, job_name, file_uri, bucket_name, patient_id, encounter_id, assessment_id)

        return True
    except Exception as e:
        error_message = f"ERROR : {str(e)} and Line no. : {e.__traceback__.tb_lineno}"
        error_dict = {
                "message": error_message,
                "description": f"error has been raised while storing the merged audio file to single named audio folder."
            }
        print(error_dict)
        raise e


# ---------------------------------------------------------------------
# AWS Transcribe Medical
# ---------------------------------------------------------------------
def start_transcription_job(slack_client, job_name, file_uri, output_bucket_name, patient_id, encounter_id, assessment_id):
    """
    AWS Medical Transcribe Job Submission
    """
    try:
        response = transcribe_client.start_medical_transcription_job(
            MedicalTranscriptionJobName=job_name,
            Media={'MediaFileUri': file_uri},
            OutputBucketName=output_bucket_name,
            OutputKey=f'transcription/{patient_id}/{encounter_id}/{assessment_id}/',
            Settings={
                'ShowSpeakerLabels': True,
                'MaxSpeakerLabels' : 2,
                'ChannelIdentification': False
            },
            LanguageCode='en-US',
            Specialty="PRIMARYCARE",
            Type="CONVERSATION"
        )
        return response
    except Exception as e:
        # Send an Alert to Slack Channel
        slack_message = f"Something went wrong while creating aws medical transcribe job.\n\nDate : *{time.ctime(time.time())}*\nPatient ID : *{patient_id}*\nEncounter ID : *{encounter_id}*\nAssessment ID : *{assessment_id}*\nError : *{str(e)}*\nLine No. : *{e.__traceback__.tb_lineno}*"
        send_message_to_slack_channel(slack_client=slack_client, channel_name=slack_channel_name, message=slack_message)
        raise e


# ---------------------------------------------------------------------
# Main Function Handler
# ---------------------------------------------------------------------

def lambda_handler(event, context):
    try:

        logger.info("Received event: %s", json.dumps(event))        

        body = event.get("body")

        data_dict = json.loads(body)

        patient_id = data_dict.get("patient_id")
        encounter_id = data_dict.get("encounter_id")
        assessment_id = data_dict.get("assessment_id")
        assessment_type = data_dict.get("assessment_type")

        if not patient_id:
            patient_id = ""
        if not encounter_id:
            encounter_id = ""
        if not assessment_id:
            assessment_id = ""
        if not assessment_type:
            assessment_type = ""

        # Create Slack Client
        slack_bot_token = get_secret_by_name(secret_key_name="SLACK_BOT_TOKEN")
        slack_client = WebClient(token=slack_bot_token)

        # Send an Alert to Slack Channel
        slack_message = f"Process Started.\n\nDate : *{time.ctime(time.time())}*\nPatient ID : *{patient_id}*\nEncounter ID : *{encounter_id}*\nAssessment ID : *{assessment_id}*"
        send_message_to_slack_channel(slack_client=slack_client, channel_name=slack_channel_name, message=slack_message)

        # if testing_flag:
        #     return "Triggered testing flag..."
        
        # Constants
        all_raw_objects_folder_path = f"raw/{patient_id}/{encounter_id}/"
        single_recording_object_folder_path = f"single/{patient_id}/{encounter_id}/"
        
        # Get all object list from s3
        object_key_list = list_s3_folder_contents(folder_name=all_raw_objects_folder_path)

        # Sort object key list based on timestamp
        sorted_objects_key_list = get_sorted_object_key_for_merging(object_key_list = object_key_list)
        
        # Create a combined audio object
        combined_audio = create_combined_audio_from_chunks(sorted_objects_key_list=sorted_objects_key_list)

        # Store combined audio to s3
        status = create_single_audio_file_and_save_to_s3(slack_client, combined_audio=combined_audio, single_recording_object_folder_path=single_recording_object_folder_path, patient_id=patient_id, encounter_id=encounter_id, assessment_id=assessment_id)
        print(f"STATUS for {patient_id}/{encounter_id}/{assessment_id} : ", status)

        message = "Completed whole process(merging, saving and creating transcription job) successfully."
        print(message)
        return {
            'statusCode': 200,
            "headers": {
                "Access-Control-Allow-Origin": "*", 
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            'body': json.dumps(message),
        }
        
    except Exception as e:
        error_message = f"Something went wrong while processing(merging, saving and creating transcription job) and Error : {str(e)} & Line No.- {e.__traceback__.tb_lineno}"
        logger.error(error_message)

        # Send an Alert to Slack Channel
        slack_message = f"Something went wrong while processing(merging, saving and creating transcription job).\n\nDate : *{time.ctime(time.time())}*\nPatient ID : *{patient_id}*\nEncounter ID : *{encounter_id}*\nError : *{str(e)}*\nLine No. : *{e.__traceback__.tb_lineno}*"
        send_message_to_slack_channel(slack_client=slack_client, channel_name=slack_channel_name, message=slack_message)

        return {
            'statusCode': 400,
            'body': json.dumps(error_message),
        }
    
if __name__ == "__main__":
    print(f"Starting merge_audio from main")
    