import os
from gpt_api import gpt_request

previous_response_id = None

while True:
    user_input = input("You: ")
    
    # Call the GPT request function
    response, previous_response_id = gpt_request(user_input, previous_response_id)
    
    print("AI:", response)
