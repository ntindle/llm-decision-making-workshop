# LLM Decision Making Workshop

This project demonstrates an AI-powered robot control system using Anthropic's Claude API for image analysis and decision-making.

## Features

- Captures images from a camera
- Analyzes images using Claude AI
- Makes decisions for robot movement based on AI analysis
- Supports custom goals for the robot
- Saves debug images for each run

## Prerequisites

- Python 3.12+
- Poetry for dependency management
- Anthropic API key
- Webcam or camera connected to your computer

## Installation

1. Install [Python 3.12+](https://www.python.org/downloads/)
2. Install [Poetry](https://python-poetry.org/docs/#installation)
3. Clone the repository:

   ```bash
   git clone https://github.com/ntindle/llm-decision-making-workshop.git
   cd llm-decision-making-workshop
   ```

4. Install dependencies using Poetry:

   ```bash
   poetry install
   ```

5. Copy the `.env.example` file to `.env` and add your Anthropic API key:

   ```bash
   cp .env.example .env
   ```

   Then edit the `.env` file and replace `<your_anthropic_api_key>` with your actual API key.

## Usage

1. Activate the Poetry environment:

   ```bash
   poetry shell
   ```

2. Run the main script:

   ```bash
   python llm_workshop/main.py
   ```

3. Enter a goal for the robot when prompted (e.g., "go to the kitchen").

4. The program will start capturing images from your camera, analyzing them with Claude AI, and making decisions for robot movement.

5. Debug images will be saved in the `debug` folder for each run.

6. The program will continue running until the AI decides the task is complete or you manually stop it (Ctrl+C).

## Customization

- Modify the `tools` list in `llm_workshop/main.py` to add or change available robot actions.
- Adjust the camera settings or image processing in the `capture_image_from_camera()` function if needed.
- Change the Claude model or other API parameters in the `analyze_image()` function.

## Troubleshooting

- If you encounter camera-related issues, make sure your webcam is properly connected and recognized by your system.
- Check your Anthropic API key if you experience authentication errors.
- Ensure you have sufficient API credits for running multiple iterations of image analysis.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
