# Voice Mode1

Voice Mode1 is a voice-controlled assistant bot that uses the OpenAI API (ChatGPT) for chat completion and interacts with the user through voice commands and responses.

## Features

- Fetches weather data and news headlines
- Generates daily reports
- Records audio and stops recording when silence is detected or the maximum duration is reached
- Transcribes audio
- Converts text to speech

## Libraries Used

- geocoder
- openai
- time
- numpy
- sounddevice
- pygame
- soundfile
- os
- requests
- vlc

## Setup

1. Define variables for the OpenAI API key (`api_key`) and the weather API key (`weatherAPI`).
2. Initialize the OpenAI client using the provided API key.

## Usage

Create an instance of the `assistantbot` class and start the bot in the inactive state by calling the `inactive_state()` method.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
