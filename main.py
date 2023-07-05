import os
import argparse
from gpt_api import gpt_request

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Chat with the AI using OpenAI GPT')
parser.add_argument('-model', dest='model', type=str, default='gpt-3.5-turbo',
                    help='Specify the GPT model to use')
args = parser.parse_args()

previous_response_id = None

while True:
    user_input = input("You (enter 'q' to quit): ")
    
    if user_input.lower() == 'q':
        break
    
    # Call the GPT request function
    response, previous_response_id = gpt_request(user_input, previous_response_id, model_requested=args.model)
    
    print("AI:", response)
