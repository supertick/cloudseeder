import logging
import openai
from ai_core.config import settings
from ai_core.slack import send_slack_message
from itertools import zip_longest
from concurrent.futures import ThreadPoolExecutor
import json
import tempfile
import io
import os
import time

# FIXME - put in config
delete_openai_objects = False
number_of_question = 5


# Constants
INSTRUCTIONS = """
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
    "question_text": "Indicate the patient's usual ability with everyday activities prior to the current illness, exacerbation, or injury. - Code the patient's need for assistance with bathing, dressing, using the toilet, and eating prior to the current illness, exacerbation, or injury.",
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
        

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

    
def get_splitted_assessment_list()-> list:
    """
    Get Splitted Assessment list by assessment_object_key
    """
    # file_content = get_s3_object_content(object_key=assessment_object_key)
    with open("questions.json", "r") as json_file:
        file_content = json.load(json_file)
        assessment_raw_list = json.loads(file_content)
        assessment_splitted_list = [t for t in zip_longest(*[iter(assessment_raw_list)]*number_of_question, fillvalue=None) if all(v is not None for v in t)]
        return assessment_splitted_list
    

# Define a helper function to split the assessment list into chunks
def split_assessment_list(assessment_list, chunk_size):
    """Splits a list into chunks of a given size."""
    return [assessment_list[i:i + chunk_size] for i in range(0, len(assessment_list), chunk_size)]

# Define a helper function to prepare user content
def prepare_user_content(splitted_list, template):
    """Prepares user content by replacing placeholders in the template."""
    user_content_list = []
    for item in splitted_list:
        user_content_copy = str(template)
        user_content_list.append(user_content_copy.replace("question_list_in_json", json.dumps(item)))
    return user_content_list


def answer_questions(conversation_data:dict, patient_id: str, encounter_id: str, assessment_id: str):

    # FIXME - change to database call to get assessment list
    with open("questions.json", "r") as file:
        full_assessment_list = json.load(file)
    logger.info(f"full_assessment_list: {len(full_assessment_list)} items")

    client = openai.OpenAI(api_key=settings.openai_key)

    try:
        # ---------------------------------------------------------------
        # OpenAI Operation
        # ---------------------------------------------------------------
        vector_store_name = f"vs_{patient_id}"
        assistant_name = f"assistant_{patient_id}"
                    
        # Create Vector Store
        vector_store = client.beta.vector_stores.create(name=vector_store_name)

        # Convert dict to JSON
        json_content = json.dumps(conversation_data)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            temp_file.write(json_content.encode("utf-8"))
            temp_file_path = temp_file.name

        # Use the filename in file_paths
        file_paths = [temp_file_path]
        file_streams = [open(path, "rb") for path in file_paths]


        # # Create an in-memory file
        # file_stream = io.BytesIO(json_content.encode("utf-8"))
        
        # # Upload file to OpenAI first, then reference it
        # uploaded_file = client.files.create(
        #     file=file_stream,  # Pass the in-memory file
        #     purpose="assistants"
        # )

        # Upload File to Vector Store
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id,
            files=file_streams  # Use OpenAI File ID
        )

        logger.info(f"File batch status: {file_batch.status}")
        logger.info(f"File batch counts: {file_batch.file_counts}")

        # Create Assistant
        assistant = create_openai_assistant(
            client=client,
            assistant_name=assistant_name,
            instructions=INSTRUCTIONS,
            openai_model=settings.openai_model,
            vector_store_id=vector_store.id
        )

        chunk_size = number_of_question  # Number of questions per chunk
        assessment_splitted_list = split_assessment_list(full_assessment_list, chunk_size)
        user_content_list = prepare_user_content(assessment_splitted_list, user_content_default)

        question_answer_list = []

        # Parallel processing with ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            futures = []
            for user_content in user_content_list:
                future = executor.submit(get_llm_response, client, assistant.id, user_content)
                futures.append(future)

            # Collect results from futures
            question_answer_list = []
            run_obj_list = []

            for future in futures:
                try:
                    data_dict = future.result()

                    # Get run object and append to a list
                    run_object = data_dict.get("run_object")
                    run_obj_list.append(run_object)

                    # Get response and convert it into JSON
                    response = data_dict.get("response")
                    if response and response.find("Robert") != -1:
                            print("The string contains 'Robert'.")

                    if response:
                        string = response.replace("```", "").replace("json", "").strip()

                        try:
                            json_data = json.loads(string)
                        except Exception as e:
                            try:
                                json_data = format_json_response_using_llm(client=client, raw_string=string)
                            except Exception as e:
                                json_data = []
                        finally:
                            for item in json_data:
                                question_answer_list.append(item)
                except Exception as e:
                    logger.error(f"Error processing future: {e}")            
                            
        # Send an Alert to Slack Channel
        slack_message = (f"Whole process completed successfully with Question-Answer pair.\n\n"
        f"Date : *{time.ctime(time.time())}*\n"
        f"Patient ID : *{patient_id}*\n"
        f"Encounter ID : *{encounter_id}*\n"
        f"Assessment ID : *{assessment_id}*")

        send_slack_message(slack_message)

        final_data_dict = {
            "EncounterID": encounter_id,
            "PatientID": patient_id,
            "Responses": question_answer_list
        }

        # logger.debug(f"final_data_dict: {final_data_dict}")
        return final_data_dict
                
    except Exception as e:
        # Send an Alert to Slack Channel
        error_message = (
            f"Something went wrong while generating question-answer file.\n\n"
            f"Date : *{time.ctime(time.time())}*\n"
            f"Patient ID : *{patient_id}*\n"
            f"Encounter ID : *{encounter_id}*\n"
            f"Assessment ID : *{assessment_id}*\n"
            f"Error : *{str(e)}*\n"
            f"Line no. : *{e.__traceback__.tb_lineno}*"
        )

        logger.error(error_message)
        send_slack_message(error_message)
        return None
        

def main():
    try:
        with open(os.path.join("tests","data","conversation.json"), "r", encoding="utf-8") as file:
            conversation_data = json.load(file)    
            answers = answer_questions(conversation_data, patient_id="kate", encounter_id="encounter-1", assessment_id="assessment-1")
            print(answers)
            with open(os.path.join(f"answers-{time.time()}.json"), "w", encoding="utf-8") as file:
                json.dump(answers, file)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
