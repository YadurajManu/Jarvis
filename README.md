# J.A.R.V.I.S - Just A Rather Very Intelligent System

A voice-controlled AI assistant inspired by Iron Man's JARVIS, built with Python and Google's Gemini API.

## Features

- **Voice Recognition**: Interact with Jarvis using natural speech
- **AI-Powered Responses**: Utilizes Google's Gemini API for intelligent conversations
- **System Information**: Get details about your computer's CPU, memory, and network
- **Web Integration**: Search the web, look up Wikipedia articles, and more
- **Task Management**: Create notes and set reminders
- **Custom Protocols**: Define and run sequences of commands
- **Interruption Handling**: Interrupt Jarvis mid-explanation when needed
- **British Butler Personality**: Responds with the formal, witty style of the movie character

## Requirements

- Python 3.7+
- Internet connection (for API calls and web features)
- Microphone (for voice commands)
- Speakers (for voice responses)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/jarvis.git
   cd jarvis
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Get a Google Gemini API key:
   - Visit [Google AI Studio](https://ai.google.dev/)
   - Create an API key
   - Replace `YOUR_GEMINI_API_KEY` in the code with your actual key

## Usage

1. Run the assistant:
   ```
   python jarvis.py
   ```

2. Speak to Jarvis using commands like:
   - "Jarvis, what time is it?"
   - "Hey Jarvis, tell me a joke"
   - "Jarvis, what's the weather like today?"
   - "Jarvis, search Wikipedia for quantum computing"
   - "Jarvis, remind me to call John at 3 PM"
   - "Jarvis, take a note: Remember to buy groceries"

3. Define custom protocols:
   - "Jarvis, define protocol morning routine as tell me the time, tell me the weather, read my emails"
   - "Jarvis, run protocol morning routine"

## Customization

- Change the user name and title in the `JarvisAssistant` initialization
- Add new features by extending the `features` dictionary
- Modify Jarvis's personality by adjusting the speech patterns

## Extending Functionality

The code includes placeholders for several features that require additional setup:
- Weather information (requires OpenWeatherMap API)
- Email functionality (requires email credentials)
- Music playback (requires media player integration)
- Translation (requires translation API)
- Camera activation and screenshots (requires system-specific implementation)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by the J.A.R.V.I.S. AI from the Iron Man movies
- Powered by Google's Gemini API
- Uses various Python libraries for speech recognition, text-to-speech, and system monitoring 