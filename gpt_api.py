import openai
import yaml
from datetime import datetime
from bq import db
from keys_lib import decrypt_data
import os

def gpt_request(user_message, previous_response_id, model_requested="gpt-3.5-turbo"):#, **kwargs)

    if not openai.api_key:
        config = yaml.safe_load(open("bqconfig.yml"))
        with open(os.path.expanduser(config["enc_api_key"]), "r") as f:
            enc_api_key = f.read().strip()
        openai.api_key = decrypt_data(enc_api_key).decode("utf-8")

    # Record new message to the db
    role = "user"
    message_id = db("record_message", role=role, message=user_message)

    # Build messages
    messages = []
    if previous_response_id is not None:
        stacked_message_ids = db("get_new_stacked_ids_array", previous_response_id=previous_response_id)
        stacked_messages = db("get_stacked_message_texts", stacked_message_ids)
        for msg in stacked_messages:
            role, content = msg
            messages.append({"role": role, "content": content})
    else: stacked_message_ids = []
    messages.append({"role": "user", "content": user_message})

    # Check kwargs and prepare them as parameters for GPT call
    """gpt_kwargs = {}
    for key, value in kwargs.items():
        # Add any additional checks or processing for specific keyword arguments
        gpt_kwargs[key] = value
    """
    try:
        # Create the chat completion request
        completion = openai.ChatCompletion.create(
            model=model_requested,
            messages=messages
            #,**gpt_kwargs  # Pass the keyword arguments to the API call
        )
        
        # Record response table to the messages table
        role = "assistant"
        response = completion.choices[0].message.content
        response_id = db("record_message", role=role, message=response)

        # Record response data via log_request action
        timestamp = datetime.utcnow()
        db(
            "log_request",
            user_message_id=message_id,
            stacked_message_ids=stacked_message_ids,
            response_id=response_id,
            model_requested=model_requested,
            completion_id=completion.id,
            finish_reason=completion.choices[0].finish_reason,
            created=completion.created,
            model_used=completion.model,
            usage_completion_tokens=completion.usage.completion_tokens,
            usage_prompt_tokens=completion.usage.prompt_tokens,
            usage_total_tokens=completion.usage.total_tokens,
            stampUTC=timestamp
        )

        # Return response text and its ID
        return response, response_id

    except openai.OpenAIError as e:
        print(f"OpenAI API error: {str(e)}")
        # Handle the error as needed, such as logging, retrying, or returning a default response
        # You can also raise the exception again to propagate it to the caller if desired

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Additional error handling if needed
