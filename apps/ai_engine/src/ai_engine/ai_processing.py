# Imports
import tempfile 
from itertools import zip_longest
import json
import boto3
import requests
import os
import base64
import io
import time
import openai
from concurrent.futures import ThreadPoolExecutor
import threading

# Encryption imports
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

from slack_sdk import WebClient

# Import Environment Variables
bucket_name = os.environ.get("BUCKET_NAME")
secret_store = os.environ.get("SECRET_STORE_NAME")
assessment_object_key = os.environ.get("ASSESSMENT_FILE_PATH")
openai_model = os.environ.get("OPENAI_MODEL_NAME")
delete_openai_objects = bool(int(os.environ.get("DELETE_OPENAI_OBJECTS")))
number_of_question = int(os.environ.get("NUMBER_OF_QUESTIONS_IN_BATCH"))
slack_channel_name = os.environ.get("SLACK_CHANNEL_NAME")
delete_single_audio_file = bool(int(os.environ.get("DELETE_SINGLE_AUDIO_FILE")))

# Salesforce Varibles
salesforce_client_id = os.environ.get("SALESFORCE_CLIENT_ID")
salesforce_client_secret = os.environ.get("SALESFORCE_CLIENT_SECRET")
salesforce_username = os.environ.get("SALESFORCE_USERNAME")
salesforce_password = os.environ.get("SALESFORCE_PASSWORD")

salesforce_login_url = os.environ.get("SALESFORCE_LOGIN_URL")
salesforce_create_content_version_url = os.environ.get("SALESFORCE_CREATE_CONTENTVERSION_URL")
salesforce_get_content_document_url = os.environ.get("SALESFORCE_GET_CONTENT_DOCUMENT_URL")
salesforce_create_content_document_link_url = os.environ.get("SALESFORCE_CREATE_CONTENT_DOCUMENT_LINK_URL")

# Constants
instructions = """
You are an expert system designed to extract relevant information/answer from conversations between clinician and patient.
Given a set of questions from the user, you will analyze the transcript and provide concise answers to the user's questions based on the information present in the conversation.
"""

user_content_default = """
### Objective : 
Extract relevant answers from the conversation file for each question listed below.\n\n

### Additional Instructions :
- Do not extract the questions from the conversation file.
- If answer not found in conversation, then answer should be "Not Available".\n\n

### Output Instructions :
1. The output should be in JSON format, with each item containing the following:
    - Question code
    - Question text
    - Answer Context which is the raw answer spoken by patient in conversation
    - Relevant sweet and sort answer extracted from the conversation
    - Relevant answer's code if provided (Should be selected from given options)
2. Your responses should be tailored to the specific questions asked and should include only the pertinent details from the transcript, 
avoiding any unnecessary or irrelevant information.
3. You have to extract answers or relevant information only from conversations, not other than this.
4. If you not found any relevant information or answer, You have to just response with 'Not Available' in Answer context and Answer text.
5. You don't have to put like this keywords : ["patient wants to say", "patient mentioned in conversation"], instead of this, Answer text should be sweet and sort.
6. Relevant option should be extracted based on given options and relevant answer.\n\n

### Output Format :
- The output format is for reference only. Don't take any information from the examples provided : 
```
[
  {
    "question_code": "M1745",
    "question_text": "Any physical, verbal, or other disruptive/dangerous symptoms that are injurious to self or others or jeopardize personal safety?",
    "answer_context": "No, I never seen any symptoms that are injurious.",
    "answer_text": "No",
    "answer_code": "0"
  },
  {
    "question_code": "GG0100",
    "question_text": "Indicate the patient's usual ability with everyday activities prior to the current illness, exacerbation, or injury. - Code the patient’s need for assistance with bathing, dressing, using the toilet, and eating prior to the current illness, exacerbation, or injury.",
    "answer_context": "Yes, I completed all the activities by myself without an assitive device.",
    "answer_text": "Independent",
    "answer_code": "3"
  }
]
```\n\n

## Questions :
```
question_list_in_json
```
"""


# Create a AWS Service Clients
s3_client = boto3.client('s3')
secret_client = boto3.client('secretsmanager')


# ==========================================================================
# UTILITY FUNCTIONS
# ==========================================================================
def get_object_key_from_event(event: dict) -> str:
    """
    Get Object key from Lambda Event
    """
    try:
        object_key = event['Records'][0]['s3']['object']['key']
        # object_key = event['object_key']
        return object_key
    except Exception as e:
        raise e
        
def get_patient_id_and_encounter_id_from_object_key(key:str) -> dict:
    """
    Get Patient Id and Encounter Id from Object Key
    """
    try:
        splitted_key = key.split("/")
        if splitted_key:
            patient_id = splitted_key[1]
            encounter_id = splitted_key[2]
            assessment_id = splitted_key[3]
            return {"patient_id": patient_id, "encounter_id": encounter_id, "assessment_id": assessment_id}
    except Exception as e:
        raise e
        
def extract_data_from_file_content(file_content)->dict:
    """
    Extract data from transcription file content and
    Create a file which should be uploaded to OpenAI
    """
    try:
        json_data = json.loads(file_content)
        
        results = json_data['results']
    
        json_list = results['items']
    
        new_data_list = list()
        previous_speaker = None
        temp_content = ""
        start_time = None
        
        for data_dict in json_list:
            try:
                content = data_dict['alternatives'][0]['content']
                speaker = data_dict['speaker_label']
                
                if not previous_speaker:
                    previous_speaker = speaker
                elif previous_speaker != speaker:
                    new_data_list.append({
                        "speaker" : previous_speaker,
                        "time" : start_time,
                        "speech" : temp_content.strip(),
                    })
                    previous_speaker = speaker
                    temp_content = ""
                    start_time = None
                
                if data_dict.get('start_time') and not start_time:
                    start_time = data_dict['start_time']
            
                data_type = data_dict['type']
            
                if data_type == "punctuation":
                    temp_content = temp_content[:-1]
                temp_content += content + " "
                
            except Exception as e:
                continue
            
        return json.dumps(new_data_list)
    except Exception as e:
        raise e
        
def get_file_from_s3_and_upload_to_openai(client, slack_client, slack_channel_name: str, object_key: str, filename: str, patient_id: str = None, encounter_id: str = None, assessment_id: str = None):
    """
    Get File from s3 using object key
    Format the transcription file if format is True
    Upload the file to OpenAI
    """
    try:
        splitted_filename_list = filename.split(".")
        prefix = f"{splitted_filename_list[0]}_"
        suffix = f".{splitted_filename_list[1]}"
        
        # Get File Object Content
        file_content = get_s3_object_content(object_key=object_key)
        
        if file_content:
            # Extract Formatted Data from File Content
            file_content = extract_data_from_file_content(file_content=file_content)
            file = tempfile.NamedTemporaryFile(mode='w', prefix=prefix, suffix=suffix)
                
            file.write(file_content)
            file.seek(0)
            
            # Upload Formatted Transcription File to s3
            object_key = f"formatted_transcription/{patient_id}/{encounter_id}"
            formatted_filename = "formatted_transcription.json"
            upload_file_to_s3(object_key=object_key, file_name=formatted_filename, file_content=file_content)
            
            if file_content:
                # Upload formatted transcription text file to salseforce
                upload_transcription_text_file_to_salesforce(slack_client=slack_client, slack_channel_name=slack_channel_name, file_content=file_content, assessment_id=assessment_id)
                
                # Upload Transcription File to OpenAI
                file_obj = upload_file_in_openai(client=client, file=file)
                
                file.close()
                return file_obj
                
            file.close()
            
        return False
        
    except Exception as e:
        print(str(e))
        return False

def get_splitted_assessment_list(assessment_object_key: str, number_of_question: int)-> list:
    """
    Get Splitted Assessment list by assessment_object_key
    """
    try:
        file_content = get_s3_object_content(object_key=assessment_object_key)
        assessment_raw_list = json.loads(file_content)
        assessment_splitted_list = [t for t in zip_longest(*[iter(assessment_raw_list)]*number_of_question, fillvalue=None) if all(v is not None for v in t)]
        return assessment_splitted_list
    except Exception as e:
        raise e
    
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
        raise e

def convert_seconds_to_formatted_time(total_seconds: float):
    """
    Converts the total seconds to HH:MM:SS formatted time
    """
    try:
        total_seconds = float(total_seconds)
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02.0f}"
    except Exception as e:
        print(e)
        raise e
    
    
# ==========================================================================
# ENCRYPTION
# ==========================================================================
def create_encrypted_audio_and_save_to_s3(salt_string: str, encryption_password: str, patient_id: str, encounter_id: str):
    """
    Generates key based on salt
    Creates encrypted audio
    save it to aws s3
    """
    try:
        # Generate Key
        salt = salt_string.encode("utf-8")
        salt = base64.b64decode(salt)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(encryption_password.encode())
        
        # Get Single audio file content    
        single_audio_file_key = f"single/{patient_id}/{encounter_id}/audio_file.wav"
        single_audio_file_content = get_s3_object_content(object_key=single_audio_file_key)
        
        # Encryption
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(single_audio_file_content) + padder.finalize()
        encrypted_data_without_iv = encryptor.update(padded_data) + encryptor.finalize()
        encrypted_data = iv + encrypted_data_without_iv
        
        # Upload Encrypted Data to AWS S3
        object_key = f"encrypted/{patient_id}/{encounter_id}"
        file_name = "encrypted_audio.wav"
        file_content = io.BytesIO(salt + encrypted_data)
        upload_file_to_s3(object_key=object_key, file_name=file_name, file_content=file_content)
        
        # Delete single audio file
        if delete_single_audio_file:
            delete_file_from_s3(object_key=single_audio_file_key)
        
    except Exception as e:
        print("ERROR : ", e)
        print("LINE no. : ", e.__traceback__.tb_lineno)


# ==========================================================================
# Sending Files to Salesforce
# ==========================================================================
def get_access_token():
    """
    Get access token for the salesforce API
    """
    try:
        payload = {
            "grant_type" : "password",
            "client_id" : salesforce_client_id,
            "client_secret" : salesforce_client_secret,
            "username" : salesforce_username,
            "password" : salesforce_password,
        }
        
        response = requests.post(url=salesforce_login_url, data=payload)
        
        if int(response.status_code) in {200, 201, 202}:
            response_json = response.json()
            access_token = response_json['access_token']
            token_type = response_json['token_type']
            
            if token_type and access_token:
                token = token_type + " " + access_token
                return {"status_code" : 200, "token": token}
        return {"error": response.text, "status_code" : response.status_code}
        
    except Exception as e:
        return {"error": str(e), "status_code" : 400}
        
        
def create_content_version(file_data, token: str, assessment_id: str):
    """
    Create Content Version
    """
    try:
        if isinstance(file_data, dict):
            file_data = json.dumps(file_data)
            file_name = f'QA-{assessment_id}.json'
        else:
            file_name = f'TR-{assessment_id}.txt'
            
        base64_data = base64.b64encode(file_data.encode('utf-8')).decode('utf-8')
        
        payload = {
            'Title': file_name,
            'ContentLocation': 'S',
            'PathonClient': file_name,
            'VersionData': base64_data,
        }
        
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(salesforce_create_content_version_url, headers=headers, json=payload)
        
        if int(response.status_code) in {200, 201, 202}:
            response_json = response.json()
            if response_json['success']:
                content_document_id = response_json['id']
                return {"status_code" : 200, "content_document_id": content_document_id}
                
            return {"error": response_json['errors'][0], "status_code" : 400}
        return {"error": response.text, "status_code" : response.status_code}
    except Exception as e:
        return {"error": str(e), "status_code" : 400}
    
    
def get_content_document(content_document_id: str, token: str):
    """
    Get Content Document
    """
    try:
        query_value = f"'{content_document_id}'"
        
        url = salesforce_get_content_document_url + query_value
        
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        
        if int(response.status_code) in {200, 201, 202}:
            response_json = response.json()  # {'totalSize': 1, 'done': True, 'records': [{'attributes': {'type': 'ContentVersion', 'url': '/services/data/v58.0/sobjects/ContentVersion/068a5000002TVs7AAG'}, 'ContentDocumentId': '069a5000002ec8hAAA'}]}
            
            if response_json['done'] and response_json['records'] and response_json['totalSize']:
                salesforce_content_document_id = response_json['records'][0]['ContentDocumentId']
                return {"status_code" : 200, "salesforce_content_document_id": salesforce_content_document_id}
                
            return {"error": "not found any document", "status_code" : 400}
        return {"error": response.text, "status_code" : response.status_code}
        
    except Exception as e:
        return {"error": str(e), "status_code" : 400}
        
    
def create_content_document_link(salesforce_content_document_id: str, assessment_id : str, token: str):
    """
    Get Content Document
    """
    try:
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        
        payload = {
            "ContentDocumentId": salesforce_content_document_id,
            "LinkedEntityId": assessment_id,
            "Visibility": "AllUsers"
        }
        
        response = requests.post(url=salesforce_create_content_document_link_url, json=payload, headers=headers)
        
        if int(response.status_code) in {200, 201, 202}:
            response_json = response.json()
            if response_json['success']:
                id = response_json['id']
                return {"status_code" : 200, "id": id}
            return {"error": response_json['errors'][0], "status_code" : 400}
        return {"error": response.text, "status_code" : response.status_code}
        
    except Exception as e:
        return {"error": str(e), "status_code" : 400}
        
        
def upload_file_to_salesforce(slack_client, slack_channel_name: str, file_data, assessment_id: str):
    """
    Upload a file to salesforce
    """
    try:
        login_resp_dict = get_access_token()
        
        if login_resp_dict["status_code"] == 200:
            access_token = login_resp_dict['token']
        
            # Create Content Version
            content_version_resp_dict = create_content_version(file_data=file_data, token=access_token, assessment_id=assessment_id)
            
            if content_version_resp_dict['status_code'] == 200:
                content_document_id = content_version_resp_dict['content_document_id']
                
                # Get Content Document
                content_document_resp_dict = get_content_document(content_document_id = content_document_id, token = access_token)
            
                if content_document_resp_dict['status_code'] == 200:
                    salesforce_content_document_id = content_document_resp_dict['salesforce_content_document_id']
                    
                    # Create Content Document Link
                    content_document_link_resp_dict = create_content_document_link(salesforce_content_document_id=salesforce_content_document_id, assessment_id=assessment_id, token=access_token)
                
                    if content_document_link_resp_dict['status_code'] == 200:
                        id = content_document_link_resp_dict['id']
                        
                        if isinstance(file_data, dict):
                            file_sent_message = f"Question-Answer JSON file sent to salesforce successfully."
                        else:
                            file_sent_message = "Formatted transcription text file sent to salesforce successfully."
                        send_message_to_slack_channel(slack_client=slack_client, channel_name=slack_channel_name, message=file_sent_message)
                        return True
                    else:
                        error = content_document_link_resp_dict['error']
                else:
                    error = content_document_resp_dict['error']
            else:
                error = content_version_resp_dict['error']
        else:
            error = login_resp_dict['error']
                    
        file_upload_error_message = f"Something went wrong while uploading a file to salesforce and Error : {error}"            
        send_message_to_slack_channel(slack_client=slack_client, channel_name=slack_channel_name, message=file_upload_error_message)
        return False
    except Exception as e:
        print(e)


def upload_transcription_text_file_to_salesforce(slack_client, slack_channel_name: str, file_content, assessment_id: str):
    """
    Upload Transcription text file to Salesforce
    """
    try:
        file_data_list = json.loads(file_content)
        
        content_text = ""
        for item in file_data_list:
            try:
                total_seconds = item['time']
                formatted_time = convert_seconds_to_formatted_time(total_seconds)
            
                content_text += f"{item['speaker']} : {str(formatted_time)} : {item['speech']}\n"
            except Exception as e:
                print(e)
                continue
            
        if content_text:
            upload_file_to_salesforce(slack_client=slack_client, slack_channel_name=slack_channel_name, file_data=content_text, assessment_id=assessment_id)
        else:
            file_upload_error_message = f"Error : Transcription text file received empty."          
            send_message_to_slack_channel(slack_client=slack_client, channel_name=slack_channel_name, message=file_upload_error_message)
            
    except Exception as e:
        print("ERROR : ", e)
        
        
# ==========================================================================
# S3 OPERATIONS
# ==========================================================================
def get_s3_object_content(object_key):
    """
    Retrieve an object content from an S3 bucket using its key
    """
    try:
        obj = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        return obj['Body'].read()
    except Exception as e:
        raise e

def upload_file_to_s3(object_key:str, file_name: str, file_content: str):
    """
    """
    try:
        key = object_key + "/" + file_name
        
        # Put the file content to the specified bucket
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=file_content)
    except Exception as e:
        raise e
     
def delete_file_from_s3(object_key:str):
    """
    Delete single audio file from AWS S3
    """
    try:
        # Put the file content to the specified bucket
        s3_client.delete_object(Bucket=bucket_name, Key=object_key)
    except Exception as e:
        raise e
    
    
# ==========================================================================
# SECRET MANAGER OPERATIONS
# ==========================================================================
def get_secret_by_name(secret_key_name: str):
    """
    Retrieve an secrets from secret manager
    """
    try:
        response = secret_client.get_secret_value(SecretId=secret_store)
        secrets_dict = json.loads(response['SecretString'])
        
        if secrets_dict:
            return secrets_dict.get(secret_key_name)
            
    except Exception as e:
        raise e


# ==========================================================================
# OPEN AI FUNCTIONS
# ==========================================================================
def upload_file_in_openai(client, file) -> dict:
    """
    Upload File in OpenAI
    """
    try:
        file_obj = client.files.create(file=open(file.name, "rb"), purpose="assistants")
        return file_obj
    except Exception as e:
        raise e

def create_openai_assistant(client, assistant_name: str, instructions: str, openai_model: str, vector_store_id: str):
    """
    Create OPENAI Assistant for File Search Functionality
    
    @parameters:
        - assistant_name (str) : Assistant Name
        - instructions (str) : Instructions to Assistant
        - openai_model (str) : OpenAI's Model Name
        - vector_store_id (str) : Vector Store Id
        
    @returns:
        - OpenAI's Assistant Object
    """
    return client.beta.assistants.create(
      name=assistant_name,
      instructions=instructions,
      model=openai_model,
      tools=[{"type": "file_search"}],
      tool_resources= {
        "file_search": {
          "vector_store_ids": [vector_store_id]
        }
      },
      temperature=0.1,
    )
    
def create_thread_and_run(client, assistant_id: str, user_content: str):
    """
    Create Thread and Run for File Search Functionality
    
    @parameters:
        - assistant_id (str) : Assistant Id
        - user_content (str) : User Role's Content/Query
        
    @returns:
        - OpenAI's Run Object
    """
    return client.beta.threads.create_and_run(
          assistant_id=assistant_id,
          thread={
            "messages": [
             {
                  "role": "user",
                  "content": user_content
            }
          ]
          },
        )
        
def get_response_messages_by_thread_id(client, run_object):
    """
    Get LLM Response Message by Thread ID
    
    @parameters:
        - run_object : Run Object
        
    @returns:
        - (str) : Generated llm response
    """
    time.sleep(5)
    while True:
        run_info = client.beta.threads.runs.retrieve(thread_id=run_object.thread_id, run_id=run_object.id)
        if run_info.completed_at or run_info.failed_at:
            break
        time.sleep(1)
    
    # get bot response
    messages_after_run = list(
        client.beta.threads.messages.list(
            thread_id=run_object.thread_id, run_id=run_object.id, order="desc", limit=1
        )
    )
    
    if messages_after_run:
        message_content = messages_after_run[0].content[0].text
        return message_content.value
        
    return ""

def delete_all_openai_objects(client, file_ids_list: list, vector_store_id: str, run_ids: list, assistant_id: str):
    """
    Delete all OpenAI Objects
    """
    try:
        # Delete Uploaded Files
        for file_id in file_ids_list:
            try:
                client.files.delete(file_id)
            except Exception as e:
                continue
            
        # Delete Vector Store
        client.beta.vector_stores.delete(vector_store_id)
        
        # Delete All Messages and Thread
        for run_obj in run_ids:
            thread_id = run_obj.thread_id
            
            # Delete Messages
            thread_messages = client.beta.threads.messages.list(thread_id)
            for message in thread_messages.data:
                client.beta.threads.messages.delete(
                    message_id=message.id,
                    thread_id=thread_id
                )
                
            # Delete Thread
            client.beta.threads.delete(thread_id)
        
        # Delete Assistant
        client.beta.assistants.delete(assistant_id)
        
    except Exception as e:
        raise e
    
def get_llm_response(client, assistant_id: str, user_content: str) -> str:
    """
    Get Formatted LLM Response
    """
    # Create and Run Thread
    run = create_thread_and_run(client=client, assistant_id=assistant_id, user_content=user_content)
    
    # Get Messages from LLM
    response = get_response_messages_by_thread_id(client=client, run_object=run)

    return {"run_object": run, "response": response }
    
def format_json_response_using_llm(client, raw_string: str):
    """
    Convert to structured JSON format from string using LLM
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            response_format={ "type": "json_object" },
            messages=[
                {
                    "role": "system",
                    "content": """
    You are a helpful assistant designed to output JSON from raw string with below format : 
    
    ### OUTPUT FORMAT :
    ```
    "response" : {
        [
            {
                "question_code": <question_code>,
                "question_text": <question_text>,
                "answer_context": <answer_context>,
                "answer_text": <answer_text>,
                "answer_code": <answer_code>
            },
            {
                "question_code": <question_code>,
                "question_text": <question_text>,
                "answer_context": <answer_context>,
                "answer_text": <answer_text>,
                "answer_code": <answer_code>
            }
        ]
    }
    ```
    """
                },
                {"role": "user", "content": raw_string}
            ]
        )
        
        json_data = json.loads(response.choices[0].message.content)
    
        if "response" in json_data.keys():
            return json_data.get("response")
            
        elif "result" in json_data.keys():
            return json_data.get("result")
            
        elif "question_data" in json_data.keys():
            return json_data.get("question_data")
            
        else:
            return json_data
        
    except Exception as e:
        raise e
        
        
# ==========================================================================
# MAIN LAMBDA HANDLER
# ==========================================================================
def lambda_handler(event, context):
    """
    Main Lambda Handler
    """
    try:
        # Get Encryption Salt
        encryption_salt = get_secret_by_name(secret_key_name="ENCRYPTION_SALT")
        encryption_password = get_secret_by_name(secret_key_name="ENCRYPTION_PASSWORD")
        
        # Create a Slack Client to send Messages
        slack_bot_token = get_secret_by_name(secret_key_name="SLACK_BOT_TOKEN")
        slack_client = WebClient(token=slack_bot_token)
        
        # Create OpenAI Client
        api_key = get_secret_by_name(secret_key_name="OPENAI_API_KEY")
        
        client = openai.OpenAI(api_key=api_key)

        # Get Object key from Lambda Event 
        object_key = get_object_key_from_event(event=event)
        
        if "medical" not in str(object_key):
            return {
                'statusCode': 400,
                'error': json.dumps("There is no medical transcribe file uploaded.")
            }
        
        # Get Patient and Encounter Id from object key
        object_data_dict = get_patient_id_and_encounter_id_from_object_key(key=object_key)
        patient_id = object_data_dict.get("patient_id")
        encounter_id = object_data_dict.get("encounter_id")
        assessment_id = object_data_dict.get("assessment_id")
        
        # Send an Alert to Slack Channel
        slack_message = f"Generating Question-Answer process started.\n\nDate : *{time.ctime(time.time())}*\nPatient ID : *{patient_id}*\nEncounter ID : *{encounter_id}*\nAssessment ID : *{assessment_id}*"
        send_message_to_slack_channel(slack_client=slack_client, channel_name=slack_channel_name, message=slack_message)
        
        # ---------------------------------------------------------------
        # OpenAI Operation
        # ---------------------------------------------------------------
        vector_store_name = f"vs_{patient_id}"
        assistant_name = f"assistant_{patient_id}"
        
        # Get and Upload Transcription File
        transcription_file_obj = get_file_from_s3_and_upload_to_openai(client=client, slack_client=slack_client, slack_channel_name=slack_channel_name, object_key=object_key, filename="transcript.json", patient_id=patient_id, encounter_id=encounter_id, assessment_id=assessment_id)
        
        if not transcription_file_obj:
            # Send an Alert to Slack Channel
            slack_message = f"Transcription file found empty.\n\nDate : *{time.ctime(time.time())}*\nPatient ID : *{patient_id}*\nEncounter ID : *{encounter_id}*\nAssessment ID : *{assessment_id}*"
            send_message_to_slack_channel(slack_client=slack_client, channel_name=slack_channel_name, message=slack_message)
            return {
                'statusCode': 400,
                'error': json.dumps("Transcription file found empty.")
            }
            
        # Create Vector Store
        vector_store = client.beta.vector_stores.create(name=vector_store_name)
        
        file_batch = client.beta.vector_stores.file_batches.create_and_poll(vector_store_id=vector_store.id, file_ids=[transcription_file_obj.id])
        
        # Create Assistant
        assistant = create_openai_assistant(
            client=client,
          assistant_name=assistant_name,
          instructions=instructions,
          openai_model=openai_model,
          vector_store_id=vector_store.id
        )
        
        assessment_splitted_list = get_splitted_assessment_list(assessment_object_key=assessment_object_key, number_of_question=number_of_question)
        
        user_content_list = list()
        for item in assessment_splitted_list:
            user_content_default_copy = str(user_content_default)
            user_content_list.append(user_content_default_copy.replace("question_list_in_json", json.dumps(item)))
        
        with ThreadPoolExecutor() as executor:
            futures = []
            for user_content in user_content_list:
                future = executor.submit(get_llm_response, client, assistant.id, user_content)
                futures.append(future)
        
            # Iter in Futures to get every task's result
            question_answer_list = list()
            run_obj_list = list()
            
            for future in futures:
                try:
                    data_dict = future.result()
                    
                    # Get run object and append to a list
                    run_object = data_dict.get("run_object")
                    run_obj_list.append(run_object)
                    
                    # Get response and convert it into JSON
                    response = data_dict.get("response")
                    if response:
                        string = response.replace("```", "").replace("json", "").strip()
                        
                        try:
                            json_data = json.loads(string)
                    
                        except Exception as e:
                            try:
                                json_data = format_json_response_using_llm(client=client, raw_string=string)
                            except Exception as e:
                                json_data = list()
                                
                        finally:
                            for item in json_data:
                                question_answer_list.append(item)

                except Exception as e:
                    print("ERROR IN Results : ", str(e), " & Line No. - ", e.__traceback__.tb_lineno)
            
            # Create Required JSON Format
            final_data_dict = {
                "EncounterID": encounter_id,
                "PatientID": patient_id,
                "Responses": question_answer_list
            }
            
            if final_data_dict:
                # Upload final_data_dict to Salesforce
                upload_file_to_salesforce(slack_client=slack_client, slack_channel_name=slack_channel_name, file_data=final_data_dict, assessment_id=assessment_id)
                
                # Save JSON Data to s3
                object_key = f"question_answer/{patient_id}/{encounter_id}"
                question_answer_file_name = "question_answer.json"
                upload_file_to_s3(object_key=object_key, file_name=question_answer_file_name, file_content=json.dumps(final_data_dict))
        
        # Delete All OpenAI Objects
        if delete_openai_objects:
            delete_all_openai_objects(
                client=client,
                file_ids_list=[transcription_file_obj.id],
                vector_store_id=vector_store.id,
                run_ids=run_obj_list,
                assistant_id=assistant.id
            )
            
        # Create and Save Encrypted Audio file to s3 and Delete single audio file from s3
        create_encrypted_audio_and_save_to_s3(salt_string=encryption_salt, encryption_password=encryption_password, patient_id=patient_id, encounter_id=encounter_id)
        
        # Send an Alert to Slack Channel
        slack_message = f"Whole process completed successfully with Question-Answer pair.\n\nDate : *{time.ctime(time.time())}*\nPatient ID : *{patient_id}*\nEncounter ID : *{encounter_id}*\nAssessment ID : *{assessment_id}*"
        send_message_to_slack_channel(slack_client=slack_client, channel_name=slack_channel_name, message=slack_message)
        
        return {
            'statusCode': 200,
            'body': json.dumps("Completed...")
        }
        
    except Exception as e:
        # Send an Alert to Slack Channel
        slack_message = f"Something went wrong while generating question-answer file.\n\nDate : *{time.ctime(time.time())}*\nPatient ID : *{patient_id}*\nEncounter ID : *{encounter_id}*\nAssessment ID : *{assessment_id}*\nError : *{str(e)}*\nLine no. : *{e.__traceback__.tb_lineno}*"
        send_message_to_slack_channel(slack_client=slack_client, channel_name=slack_channel_name, message=slack_message)
        return {
            'statusCode': 400,
            'error': json.dumps("something went wrong.")
        }
        