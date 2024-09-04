import os  # For file system operations
import time  # For time-related functions
from typing import Iterable  # for Anthropic typing fun
import anthropic  # For interacting with Anthropic API
import cv2  # OpenCV for camera capture
from pydantic_settings import BaseSettings  # Import Pydantic for settings management
import base64  # Add this import at the top of the file
from command_sender import command_sender

# Define settings class
class Settings(BaseSettings):
    anthropic_api_key: str  # Define the API key setting

    class Config:
        env_file = ".env"  # Specify the environment file


# Load settings
settings = Settings()  # type: ignore

# Initialize Anthropic client with the API key
client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


def capture_image_from_camera():
    # Initialize the camera
    cap = cv2.VideoCapture(0)  # Use the first camera

    # Check if the camera opened successfully
    if not cap.isOpened():
        raise Exception("Could not open camera")

    # Wait for the camera to warm up
    time.sleep(0.5)

    # Capture a frame
    ret, frame = cap.read()

    # Release the camera
    cap.release()

    if ret:
        # Resize the frame
        resized_frame = cv2.resize(frame, (640, 480))  # Adjust size as needed

        # Convert the resized frame to PNG format
        _, img_encoded = cv2.imencode(
            ".png", resized_frame, [cv2.IMWRITE_PNG_COMPRESSION, 0]
        )
        img_byte_arr = img_encoded.tobytes()
        return img_byte_arr
    else:
        raise Exception("Could not capture image from camera")


def analyze_image(image, goal, history):
    # Encode the image data to base64
    image_base64 = base64.b64encode(image).decode("ascii")

    tools: list[anthropic.types.ToolParam] = [
        {
            "name": "move_robot",
            "description": "Move the robot forward or backward",
            "input_schema": {
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["forward", "backward"],
                        "description": "The direction to move the robot",
                    },
                    "distance": {
                        "type": "string",
                        "enum": ["short", "medium", "long"],
                        "description": "The distance to drive the robot in the direction specified",
                    },
                },
                "required": ["direction", "distance"],
            },
        },
        {
            "name": "turn_robot",
            "description": "Turn the robot in a direction",
            "input_schema": {
                "type": "object",
                "properties": {
                    "degrees": {
                        "type": "number",
                        "description": "The degrees to turn the robot with positive being right and negative being left from the current perspective",
                    },
                },
                "required": ["degrees"],
            },
        },
        {
            "name": "finish_task",
            "description": "Finish the task",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    ]

    messages: Iterable[anthropic.types.MessageParam] = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"What you know about the robot's environment is {history}",
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_base64,  # Use the base64 encoded string
                    },
                },
                {
                    "type": "text",
                    "text": f"""Analyze this image, and the history of the robot's actions, and decide which direction the robot should move. 
                    Your goal is <GOAL>{goal}</GOAL>. Make executive decisions based on the image and history. 
                    Use the tools at your disposal to make the best decision, without asking for more information as you will need to gather it by moving the robot.
                    """,
                },
            ],
        }
    ]

    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        tools=tools,
        messages=messages,
    )

    # example response
    # {
    #     "role": "assistant",
    #     "content": [
    #         {
    #             "type": "text",
    #             "text": "<thinking>To answer this question, I will: 1. Use the get_weather tool to get the current weather in San Francisco. 2. Use the get_time tool to get the current time in the America/Los_Angeles timezone, which covers San Francisco, CA.</thinking>",
    #         },
    #         {
    #             "type": "tool_use",
    #             "id": "toolu_01A09q90qw90lq917835lq9",
    #             "name": "get_weather",
    #             "input": {"location": "San Francisco, CA"},
    #         },
    #     ],
    # }
    # return history with new text content, tool use, and the tool call
    new_history = history + response.content
    print(f"new_history: {new_history}")
    # filter the response to be the tool use and text blocks no matter the order
    text_blocks = [item for item in response.content if item.type == "text"]
    tool_blocks = [item for item in response.content if item.type == "tool_use"]
    return new_history, text_blocks, tool_blocks


def save_debug_image(screenshot):
    folder_path = "debug"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    run_folder = f"debug/run{len(os.listdir(folder_path))}"
    if not os.path.exists(run_folder):
        os.makedirs(run_folder)

    file_path = f"{run_folder}/{time.time()}.png"
    with open(file_path, "wb") as f:
        f.write(screenshot)

    return file_path


def main(goal):
    history = []
    sender = command_sender()
    while True:
        # Capture image from camera
        screenshot = capture_image_from_camera()

        # Save debug image
        debug_image_path = save_debug_image(screenshot)
        print(f"Debug image saved: {debug_image_path}")

        # Analyze image and get decision
        new_history, text_blocks, tool_blocks = analyze_image(screenshot, goal, history)
        history = new_history

        if text_blocks:
            print("-----LLM Output-----")
            print(text_blocks[0].text)

        if tool_blocks:
            print()
            print("-----Tool blocks-----")
            print(tool_blocks[0].name)
            if tool_blocks[0].name == "finish_task":
                print("-----Finished task-----")
                break
            if tool_blocks[0].name == "move_robot":
                print(
                    f"-----Moving robot {tool_blocks[0].input['direction']} {tool_blocks[0].input['distance']}-----"  # type: ignore
                )
                sender.send_command(f"{tool_blocks[0].input['direction']}-{tool_blocks[0].input['distance']}")
            if tool_blocks[0].name == "turn_robot":
                print(
                    f"-----Turning robot {tool_blocks[0].input['degrees']} degrees-----"  # type: ignore
                )
                sender.send_command(f"{'left' if tool_blocks[0].input['degrees'] else 'right'}"
                                    f"-{tool_blocks[0].input['degrees']}")

        # Wait for 10 seconds before next iteration
        time.sleep(10)


if __name__ == "__main__":
    # Get the goal from the user
    goal = input("Enter the goal for the robot: ")
    if goal == "":
        goal = "go to the kitchen"
    main(goal)
