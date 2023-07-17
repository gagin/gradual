import asyncio
import os
import argparse

from gpt_api import gpt_request

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Chat with the AI using OpenAI GPT')
parser.add_argument('-model', dest='model', type=str, default='gpt-3.5-turbo',
                    help='Specify the GPT model to use')
args = parser.parse_args()

previous_response_id = None


async def gpt_request_with_progress(user_input, previous_response_id, model_requested):
    # Display progress indicator
    progress_task, dot_count = await display_progress()

    try:
        # Call the GPT request function asynchronously (Replace with your GPT request logic)
        response, new_previous_response_id = await gpt_request(user_input.strip(), previous_response_id, model_requested)

        # Remove progress indicator
        progress_task.cancel()
        print("\r" + " " * (len("Contacting OpenAI...") + dot_count), end="")  # Clear the progress indicator message

        return response, new_previous_response_id

    except asyncio.CancelledError:
        # Handle cancellation of progress indicator task
        pass

async def display_progress():
    progress = "Contacting OpenAI"
    dot_count = 0
    while True:
        print(progress + "." * dot_count, end='\r')
        dot_count += 1
        await asyncio.sleep(1/3)


def main():
    PROMPT = "You (enter empty line to send or 'q' to quit): "
    loop = asyncio.get_event_loop()
    user_input = ""
    previous_response_id = 0
    first_input = True
    while True:
        if first_input:
            line = input(PROMPT)
            first_input = False
        else:
            line = input()

        if line.lower() == 'q':
            break

        if line.strip() == "":
            if user_input.strip() != "":
                response, previous_response_id = loop.run_until_complete(gpt_request_with_progress(user_input, previous_response_id, model_requested=args.model))
                print("AI:", response)
                user_input = ""
                continue
        else:
            user_input += line + "\n"

if __name__ == "__main__":
    main()
