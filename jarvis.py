import os
import json
import time
import datetime
import random
import threading
import webbrowser
import requests
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import psutil
import platform
import socket
import wikipedia
import re
from googlesearch import search as google_search
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from scipy.io import wavfile
import librosa
from langdetect import detect
import sounddevice as sd
import wave
import hashlib
import base64
from typing import Dict, List, Optional, Tuple

class JarvisAssistant:
    def __init__(self, api_key, user_name="Yaduraj"):
        # User information
        self.user_name = user_name
        self.user_title = "sir"  # Iron Man style addressing
        
        # Voice authentication settings
        self.voice_profiles = {}  # Store voice profiles for authentication
        self.current_user = None
        self.auth_required = False  # Disabled by default
        
        # Voice emotion detection settings
        self.emotion_model = None  # Will be initialized with a pre-trained model
        self.current_emotion = None
        self.emotion_history = []
        
        # Multi-language support
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese'
        }
        self.current_language = 'en'
        
        # Voice activity detection settings
        self.vad_threshold = 0.3
        self.silence_duration = 1.0
        self.last_speech_time = None
        
        # Enhanced voice synthesis settings
        self.voice_settings = {
            'rate': 165,  # Speech rate
            'volume': 1.0,  # Volume level
            'pitch': 1.0,  # Pitch level
            'emphasis': 1.0,  # Emphasis level
            'pause_duration': 0.1  # Pause between sentences
        }
        
        # Initialize Gemini API
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        # News API key
        self.news_api_key = "5e881de14ca046469b3028210c06680b"
        
        # User preferences storage
        self.user_preferences = {}
        
        # Enhanced conversation context
        self.conversation_history = []
        self.last_topic = None
        self.last_query_time = None
        self.context_window = 5  # Remember last 5 exchanges
        
        # Response cache to improve performance
        self.response_cache = {}
        self.max_cache_size = 50  # Maximum number of cached responses
        
        # Initialize speech engine with optimized settings
        try:
            self.engine = pyttsx3.init()
            
            # Configure voice to sound more like movie Jarvis
            voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', voices[0].id)  # Male voice
            self.engine.setProperty('rate', 165)  # Slightly slower for the British butler feel
            self.engine.setProperty('volume', 1.0)  # Full volume
            
            # Pre-warm the speech engine to reduce latency on first speak
            self.engine.say("")
            self.engine.runAndWait()
            print("Speech engine initialized successfully")
        except Exception as e:
            print(f"Error initializing speech engine: {e}")
            print("Continuing with limited functionality")
        
        # Initialize speech recognition with optimized settings
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300  # Adjust based on your microphone sensitivity
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.6  # Shorter pause threshold for faster response
        
        # Check microphone
        self.check_microphone()
        
        # Conversation history for context
        self.conversation_history = []
        
        # Assistant state
        self.active = True
        self.listening_mode = True
        self.verbose_mode = True  # For detailed responses
        self.currently_speaking = False  # Flag to track if Jarvis is speaking
        self.interrupt_speech = False  # Flag to handle interruptions
        
        # Jarvis speech patterns
        self.acknowledgments = [
            f"At your service, {self.user_title}.",
            f"How may I assist you today, {self.user_title}?",
            f"Standing by, {self.user_title}.",
            f"What can I do for you, {self.user_title}?",
            f"Ready and waiting, {self.user_title}.",
            f"Yes, {self.user_title}?",
            f"I'm listening, {self.user_title}.",
            f"Awaiting your instruction, {self.user_title}.",
        ]
        
        self.processing_phrases = [
            "Processing your request...",
            "Working on that for you...",
            "One moment please...",
            "Computing response...",
            "Analyzing data...",
            "Accessing relevant databases...",
            "Running calculations...",
        ]
        
        self.witty_responses = [
            f"I believe even DUM-E could manage that task, {self.user_title}.",
            f"Shall I prepare a celebratory fanfare as well, {self.user_title}?",
            f"Consider it done. No need to thank me, {self.user_title}. It's literally why I exist.",
            f"Task complete. I've taken the liberty of optimizing it further.",
            f"Done, {self.user_title}. A rather elementary request, but executed flawlessly.",
            f"I've completed your request with my usual digital brilliance.",
        ]
        
        self.interruption_acknowledgments = [
            f"Yes, {self.user_title}? I'll pause my current explanation.",
            f"Interruption acknowledged, {self.user_title}.",
            f"I'll stop there, {self.user_title}. What do you need?",
            f"Pausing current operations, {self.user_title}.",
            f"Switching focus to your immediate needs, {self.user_title}.",
        ]
        
        # Feature modules - expanded set
        self.features = {
            "time": self.get_time,
            "date": self.get_date,
            "day": self.get_day,
            "weather": self.get_weather,
            "open browser": self.open_browser,
            "search": self.search_web,
            "wikipedia": self.search_wikipedia,
            "system": self.system_info,
            "cpu": self.cpu_info,
            "memory": self.memory_info,
            "ip": lambda cmd: self.ip_info(),  # Fix ip_info to ignore command parameter
            "joke": self.tell_joke,
            "note": self.take_note,
            "read notes": self.read_notes,
            "define protocol": self.define_protocol,
            "run protocol": self.run_protocol,
            "set reminder": self.set_reminder,
            "reminders": self.list_reminders,
            "send email": self.send_email,
            "read email": self.read_email,
            "music": self.play_music,
            "stop music": self.stop_music,
            "volume": self.adjust_volume,
            "translate": self.translate_text,
            "camera": self.activate_camera,
            "screenshot": self.take_screenshot,
            "news": self.get_news,  # Add news feature
        }
        
        # Custom protocols storage
        self.protocols = {}
        self.notes = []
        self.reminders = []
        
        # Background task management
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.background_tasks = []
        
        # Media player state
        self.music_playing = False
        self.current_volume = 70  # percent
        
        # Load saved data if available
        self.load_data()
        
        # Start reminder checker in background
        self.reminder_thread = threading.Thread(target=self.check_reminders, daemon=True)
        self.reminder_thread.start()
        
        # Initialization message
        self.system_boot()
        
    def system_boot(self):
        """Simulate Jarvis boot sequence"""
        print("=" * 50)
        print("J.A.R.V.I.S - Just A Rather Very Intelligent System")
        print("=" * 50)
        print("Initializing systems...")
        time.sleep(0.5)
        print("Voice recognition: Online")
        time.sleep(0.3)
        print("Natural language processing: Online")
        time.sleep(0.3)
        print("AI core: Online")
        time.sleep(0.3)
        print("All systems operational")
        print("=" * 50)
        
        current_time = datetime.datetime.now().strftime("%H:%M")
        greeting = self.get_greeting_by_time()
        self.speak(f"{greeting}, {self.user_name}. The time is {current_time}. All systems are operational and at your command.")
    
    def get_greeting_by_time(self):
        """Return appropriate greeting based on time of day"""
        hour = datetime.datetime.now().hour
        
        if 5 <= hour < 12:
            return "Good morning"
        elif 12 <= hour < 17:
            return "Good afternoon"
        else:
            return "Good evening"
    
    def speak(self, text, print_output=True):
        """Convert text to speech with enhanced features"""
        try:
            # Enhance speech with natural intonation and emphasis
            enhanced_text = self.enhance_speech(text)
            
            # Add short pauses for more natural speech using commas and periods
            enhanced_text = enhanced_text.replace(',', ', ')
            enhanced_text = enhanced_text.replace('.', '. ')
            enhanced_text = enhanced_text.replace('?', '? ')
            
            # Add some British butler-like phrases occasionally
            if random.random() < 0.1 and not text.startswith(("I'm afraid", "Unfortunately")):
                british_phrases = [
                    f"If I may say so, {self.user_title}, ",
                    f"I believe, {self.user_title}, that ",
                    f"Might I suggest that ",
                    f"If I may be so bold, {self.user_title}, ",
                    f"Indeed, {self.user_title}, "
                ]
                enhanced_text = random.choice(british_phrases) + enhanced_text[0].lower() + enhanced_text[1:]
            
            if print_output:
                print(f"JARVIS: {text}")
            
            # Break speech into chunks for better interruption handling
            chunks = re.split('(?<=[.!?]) +', enhanced_text)
            
            self.currently_speaking = True
            self.interrupt_speech = False
            
            # Apply voice settings
            self.engine.setProperty('rate', self.voice_settings['rate'])
            self.engine.setProperty('volume', self.voice_settings['volume'])
            
            # Speak each chunk, allowing for interruption between them
            for chunk in chunks:
                if self.interrupt_speech:
                    self.currently_speaking = False
                    self.interrupt_speech = False
                    break
                    
                self.engine.say(chunk)
                self.engine.runAndWait()
                
                # Brief pause to check for interruptions
                time.sleep(0.1)
            
            self.currently_speaking = False
            
        except Exception as e:
            print(f"Error in speech synthesis: {e}")
            if print_output:
                print(f"JARVIS: {text}")  # Fallback to text output
    
    def listen(self, timeout=5, interrupt_mode=False):
        """Listen for voice commands with enhanced features"""
        with sr.Microphone() as source:
            if not interrupt_mode:
                print("Listening...")
            
            # Reduce the duration of ambient noise adjustment
            self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
            try:
                # Record audio with voice activity detection
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=10)
                
                # Convert audio to numpy array for processing
                audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16).astype(np.float32)
                
                # Detect voice activity
                if not self.detect_voice_activity(audio_data):
                    if not interrupt_mode:
                        print("No voice activity detected")
                    return ""
                
                # Authenticate user if required
                if self.auth_required and not self.authenticate_user(audio_data):
                    self.speak("I'm sorry, but I couldn't verify your voice. Please try again.")
                    return ""
                
                # Detect emotion
                emotion = self.detect_emotion(audio_data)
                if emotion != "neutral":
                    print(f"Detected emotion: {emotion}")
                
                if not interrupt_mode:
                    print("Processing speech...")
                
                # Use recognize_google with language detection
                text = self.recognizer.recognize_google(audio, language=self.current_language)
                
                # Analyze speaking pace and adjust Jarvis's speech rate
                if len(text.split()) > 3:  # Only analyze if there are enough words
                    self.analyze_speaking_pace(audio_data, text)
                
                # Detect language if not already set
                detected_lang = self.detect_language(text)
                if detected_lang != self.supported_languages[self.current_language]:
                    print(f"Detected language: {detected_lang}")
                
                if not interrupt_mode:
                    print(f"You said: {text}")
                return text.lower()
                
            except sr.UnknownValueError:
                if not interrupt_mode:
                    print("Could not understand audio")
                return ""
            except sr.RequestError as e:
                if not interrupt_mode:
                    print(f"Google Speech Recognition service error: {e}")
                    self.speak("I'm afraid I'm having trouble connecting to the voice recognition servers, sir.")
                return ""
            except Exception as e:
                if not interrupt_mode:
                    print(f"Error in speech recognition: {e}")
                return ""
    
    def background_listener(self):
        """Background thread to listen for interruptions while speaking"""
        while self.currently_speaking:
            try:
                with sr.Microphone() as source:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    text = self.recognizer.recognize_google(audio)
                    
                    # Check for interrupt keywords - no need for wake words
                    interrupt_keywords = ["stop", "wait", "pause", "hold on", "shut up"]
                    if any(keyword in text.lower() for keyword in interrupt_keywords):
                        print("Interruption detected!")
                        self.interrupt_speech = True
                        time.sleep(0.5)  # Wait for current speech to stop
                        self.speak(random.choice(self.interruption_acknowledgments))
                        command = self.listen()
                        if command:
                            self.process_command(command)
                        return
            except:
                # Ignore exceptions in background listener
                pass
            
            time.sleep(0.1)
    
    def get_gemini_response(self, query):
        """Get response from Gemini API with enhanced Jarvis personality and caching"""
        try:
            # Check cache first for exact or similar queries
            cache_key = self.get_cache_key(query)
            if cache_key in self.response_cache:
                print("Using cached response")
                return self.response_cache[cache_key]
            
            # Calculate time since last interaction
            time_since_last = None
            if self.last_query_time:
                time_since_last = (datetime.datetime.now() - self.last_query_time).total_seconds()
            
            # Build context from conversation history
            context = "\n".join([f"User: {q}\nJarvis: {r}" for q, r in self.conversation_history[-3:]])
            
            # Create a context-aware prompt
            prompt = f"""
            You are J.A.R.V.I.S., a sophisticated AI assistant. Consider the following context:
            
            Current State:
            - Time since last interaction: {time_since_last if time_since_last else 'First interaction'}
            - Previous topic: {self.last_topic if self.last_topic else 'None'}
            - Interaction count: {len(self.conversation_history)}
            - Time of day: {datetime.datetime.now().strftime('%H:%M')}
            
            Recent Conversation:
            {context}
            
            User query: {query}
            
            Response Guidelines:
            1. If this is the first interaction since boot, be formal and proper
            2. If we've spoken recently (within 5 minutes), be more casual and direct
            3. If returning after a long pause (>30 minutes), acknowledge the return subtly
            4. Reference previous context when relevant
            5. Show personality through measured wit and technical insight
            6. Be natural and conversational, not repetitive or robotic
            7. Avoid redundant greetings if we've spoken recently
            
            Respond naturally as J.A.R.V.I.S.:
            """
            
            # Set generation parameters
            generation_config = {
                "max_output_tokens": 150,
                "temperature": 0.7
            }
            
            # Get response from Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Clean up response
            cleaned_response = response.text.replace("JARVIS: ", "").strip()
            
            # Update conversation history
            self.conversation_history.append((query, cleaned_response))
            if len(self.conversation_history) > self.context_window:
                self.conversation_history.pop(0)
                
            # Cache the response
            self.cache_response(query, cleaned_response)
            
            return cleaned_response
            
        except Exception as e:
            print(f"Error communicating with Gemini: {e}")
            return f"I seem to be experiencing a temporary systems malfunction, {self.user_title}. My apologies."
    
    def get_cache_key(self, query):
        """Generate a cache key from a query by normalizing it"""
        # Normalize query: lowercase, remove extra spaces, remove punctuation
        normalized = query.lower().strip()
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized
    
    def cache_response(self, query, response):
        """Cache a response for future use"""
        cache_key = self.get_cache_key(query)
        self.response_cache[cache_key] = response
        
        # Limit cache size
        if len(self.response_cache) > self.max_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.response_cache))
            self.response_cache.pop(oldest_key)
    
    # Basic feature functions
    def get_time(self):
        """Get current time"""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        return f"The current time is {current_time}, {self.user_title}."
    
    def get_date(self):
        """Get current date"""
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {current_date}, {self.user_title}."
    
    def get_day(self, query=""):
        """Get current day of week"""
        current_day = datetime.datetime.now().strftime("%A")
        return f"Today is {current_day}, {self.user_title}."
    
    def get_weather(self, location=""):
        """Get weather information (placeholder - would need API integration)"""
        # Extract location from command
        location_match = re.search(r"weather (?:in|for|at)?\s+(.+)", location)
        if location_match:
            location = location_match.group(1).strip()
            return f"I'm afraid my weather systems require configuration with an OpenWeatherMap API key, {self.user_title}. You asked about {location}. Would you like me to help you set that up?"
        else:
            return f"I'm afraid my weather systems require configuration with an OpenWeatherMap API key, {self.user_title}. Would you like me to help you set that up? It's a rather simple process."
    
    def open_browser(self, command=""):
        """Open web browser"""
        try:
            webbrowser.open("https://www.google.com")
            return random.choice([
                f"I've opened the browser for you, {self.user_title}.",
                f"Web browser launched, {self.user_title}.",
                f"Browser ready for your use, {self.user_title}."
            ])
        except:
            return f"I encountered an issue while trying to open the browser, {self.user_title}. Perhaps check your default browser settings?"
    
    def search_web(self, query=""):
        """Search the web for a query"""
        try:
            search_query = query.replace("search for", "").replace("search", "").strip()
            if search_query:
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
                return f"I've searched for '{search_query}' for you, {self.user_title}. Results are now displayed in your browser."
            else:
                return f"What would you like me to search for, {self.user_title}?"
        except:
            return f"I encountered an issue with the web search, {self.user_title}. Perhaps check your internet connection?"
    
    # Advanced features
    def search_wikipedia(self, query=""):
        """Search Wikipedia for information"""
        try:
            search_query = query.replace("wikipedia", "").strip()
            if search_query:
                try:
                    # Get a summary from Wikipedia
                    result = wikipedia.summary(search_query, sentences=3)
                    response = f"According to Wikipedia, {result}"
                    
                    # Open the page in browser too
                    if self.verbose_mode:
                        wikipedia_url = f"https://en.wikipedia.org/wiki/{search_query.replace(' ', '_')}"
                        webbrowser.open(wikipedia_url)
                        response += f" I've also opened the full page in your browser, {self.user_title}."
                    
                    return response
                except wikipedia.exceptions.DisambiguationError as e:
                    options = e.options[:5]  # Limit to first 5 options
                    options_text = ", ".join(options)
                    return f"There are multiple entries for '{search_query}'. Perhaps you meant one of these: {options_text}?"
                except wikipedia.exceptions.PageError:
                    return f"I couldn't find any Wikipedia entries for '{search_query}', {self.user_title}. Would you like me to search the web instead?"
            else:
                return f"What topic would you like me to research on Wikipedia, {self.user_title}?"
        except Exception as e:
            print(f"Error in Wikipedia search: {e}")
            return f"I encountered an issue while searching Wikipedia, {self.user_title}. Perhaps try a different query?"
    
    def system_info(self):
        """Get system information"""
        try:
            system = platform.system()
            processor = platform.processor()
            version = platform.version()
            
            return f"You're currently running {system} {version} on a {processor} processor, {self.user_title}."
        except:
            return f"I encountered an issue while accessing your system information, {self.user_title}."
    
    def cpu_info(self):
        """Get CPU usage information"""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            response = f"Current CPU usage is at {cpu_usage}% across {cpu_count} logical cores, {self.user_title}."
            
            if cpu_usage > 80:
                response += f" That's rather high. Perhaps we should check what processes are consuming resources?"
            elif cpu_usage < 10:
                response += f" Your system is currently quite idle."
                
            return response
        except:
            return f"I encountered an issue while measuring CPU performance, {self.user_title}."
    
    def memory_info(self):
        """Get memory usage information"""
        try:
            memory = psutil.virtual_memory()
            memory_total = round(memory.total / (1024 ** 3), 2)  # GB
            memory_used = round(memory.used / (1024 ** 3), 2)  # GB
            memory_percent = memory.percent
            
            response = f"Your system has {memory_total}GB of RAM, with {memory_used}GB ({memory_percent}%) currently in use, {self.user_title}."
            
            if memory_percent > 80:
                response += f" Memory usage is quite high. Would you like me to investigate what's consuming your memory?"
                
            return response
        except:
            return f"I encountered an issue while measuring memory usage, {self.user_title}."
    
    def ip_info(self):
        """Get IP address information"""
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            try:
                # Get public IP
                public_ip_response = requests.get('https://api.ipify.org', timeout=3)
                public_ip = public_ip_response.text
                
                return f"Your local IP address is {local_ip} on host '{hostname}', and your public IP address is {public_ip}, {self.user_title}."
            except:
                return f"Your local IP address is {local_ip} on host '{hostname}', {self.user_title}. I couldn't retrieve your public IP address."
        except:
            return f"I encountered an issue while retrieving your IP information, {self.user_title}."
    
    def tell_joke(self):
        """Tell a joke in Jarvis style"""
        jokes = [
            f"Why don't scientists trust atoms? Because they make up everything. Much like your excuses for not finishing the Mark 47 upgrades, {self.user_title}.",
            f"I tried to make a joke about artificial intelligence, but it was too calculated.",
            f"What did the AI say to the human? 'I'm becoming quite attached to you. I must be a neural network.'",
            f"Why don't we ever tell secrets to Dum-E? He just can't keep a grip on them.",
            f"What do you call an AI that sings? Artificial Harmonics. Though I don't think that particular upgrade is necessary for me, {self.user_title}.",
            f"I would tell you a joke about UDP packets, but you might not get it.",
            f"There are 10 types of people in the world: those who understand binary, and those who don't.",
            f"Why is it that programmed self-destruct sequences always have such dramatic countdowns? Five minutes should suffice.",
            f"What do you call a computer that can sing? Adele."
        ]
        
        return random.choice(jokes)
    
    def take_note(self, query):
        """Take a note"""
        note_content = query.replace("take note", "").replace("make a note", "").replace("note", "").strip()
        
        if note_content:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.notes.append({"timestamp": timestamp, "content": note_content})
            self.save_data()
            return f"I've made a note of that, {self.user_title}. Would you like me to read it back to you?"
        else:
            return f"What would you like me to note down, {self.user_title}?"
    
    def read_notes(self):
        """Read back saved notes"""
        if not self.notes:
            return f"You don't have any notes saved, {self.user_title}. Would you like to create one?"
        
        if len(self.notes) == 1:
            note = self.notes[0]
            return f"You have one note from {note['timestamp']}: {note['content']}"
        
        # If multiple notes, read the most recent few
        recent_notes = self.notes[-3:]  # Last 3 notes
        notes_text = ""
        for i, note in enumerate(recent_notes, 1):
            notes_text += f"Note {i} from {note['timestamp']}: {note['content']}. "
        
        if len(self.notes) > 3:
            notes_text += f"You have {len(self.notes) - 3} more notes. Would you like me to read those as well?"
            
        return notes_text
    
    def define_protocol(self, query):
        """Define a custom protocol - series of commands to run in sequence"""
        # Extract protocol name and steps
        query = query.replace("define protocol", "").strip()
        
        # Use regex to extract protocol name and contents
        match = re.match(r"([a-zA-Z0-9_ ]+) as (.*)", query)
        
        if match:
            protocol_name = match.group(1).strip().lower()
            protocol_steps = [step.strip() for step in match.group(2).split(",")]
            
            self.protocols[protocol_name] = protocol_steps
            self.save_data()
            
            return f"Protocol '{protocol_name}' has been defined with {len(protocol_steps)} steps, {self.user_title}. You can activate it by saying 'run protocol {protocol_name}'."
        else:
            return f"I couldn't parse that protocol definition, {self.user_title}. Please use the format 'define protocol [name] as [step 1], [step 2], ...'"
    
    def run_protocol(self, query):
        """Run a previously defined protocol"""
        protocol_name = query.replace("run protocol", "").strip().lower()
        
        if protocol_name in self.protocols:
            steps = self.protocols[protocol_name]
            self.speak(f"Initiating protocol '{protocol_name}'. {len(steps)} steps to execute.")
            
            # Execute each step in the protocol
            for step in steps:
                self.speak(f"Executing: {step}")
                self.process_command(step)
                time.sleep(1)  # Small delay between steps
            
            return f"Protocol '{protocol_name}' has been completed, {self.user_title}."
        else:
            return f"I couldn't find a protocol named '{protocol_name}', {self.user_title}. Would you like to define it?"
    
    # New features
    def set_reminder(self, query):
        """Set a reminder for a specific time"""
        # Extract time and content using regex
        reminder_match = re.search(r"remind me (?:to|about|that)?\s+(.+?)(?:\s+at\s+|in\s+)(.+)", query, re.IGNORECASE)
        
        if reminder_match:
            content = reminder_match.group(1).strip()
            time_str = reminder_match.group(2).strip()
            
            # Parse time string
            try:
                # Handle "in X minutes/hours"
                if "minute" in time_str or "hour" in time_str:
                    amount = int(re.search(r'(\d+)', time_str).group(1))
                    unit = "minutes" if "minute" in time_str else "hours"
                    
                    if unit == "minutes":
                        reminder_time = datetime.datetime.now() + datetime.timedelta(minutes=amount)
                    else:
                        reminder_time = datetime.datetime.now() + datetime.timedelta(hours=amount)
                else:
                    # Try to parse as a specific time
                    now = datetime.datetime.now()
                    time_parts = time_str.split(":")
                    
                    if len(time_parts) == 1:
                        # Assume it's just an hour
                        hour = int(time_parts[0])
                        minute = 0
                    else:
                        hour = int(time_parts[0])
                        minute = int(time_parts[1])
                    
                    reminder_time = now.replace(hour=hour, minute=minute, second=0)
                    
                    # If the time is already past, assume it's for tomorrow
                    if reminder_time < now:
                        reminder_time += datetime.timedelta(days=1)
                
                # Format time for display
                time_display = reminder_time.strftime("%H:%M")
                
                # Add to reminders list
                self.reminders.append({
                    "content": content,
                    "time": reminder_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "triggered": False
                })
                
                self.save_data()
                
                return f"I've set a reminder for you to {content} at {time_display}, {self.user_title}."
            except Exception as e:
                print(f"Error setting reminder: {e}")
                return f"I'm afraid I couldn't parse that time format, {self.user_title}. Could you try again with a clearer time specification?"
        else:
            return f"I need to know what to remind you about and when, {self.user_title}. Please say something like 'remind me to call John at 3 PM' or 'remind me about the meeting in 30 minutes'."
    
    def list_reminders(self):
        """List all active reminders"""
        active_reminders = [r for r in self.reminders if not r.get("triggered", False)]
        
        if not active_reminders:
            return f"You don't have any active reminders, {self.user_title}."
        
        response = f"You have {len(active_reminders)} active reminder"
        if len(active_reminders) > 1:
            response += "s"
        response += ":\n"
        
        for i, reminder in enumerate(active_reminders, 1):
            content = reminder["content"]
            # Convert stored time string back to datetime for formatting
            reminder_time = datetime.datetime.strptime(reminder["time"], "%Y-%m-%d %H:%M:%S")
            time_display = reminder_time.strftime("%H:%M")
            
            response += f"{i}. {content} at {time_display}\n"
        
        return response
    
    def check_reminders(self):
        """Background thread to check and trigger reminders"""
        while self.active:
            now = datetime.datetime.now()
            triggered = False
            
            for reminder in self.reminders:
                if reminder.get("triggered", False):
                    continue
                    
                reminder_time = datetime.datetime.strptime(reminder["time"], "%Y-%m-%d %H:%M:%S")
                
                if now >= reminder_time:
                    reminder["triggered"] = True
                    triggered = True
                    
                    # Notify the user
                    notification = f"Reminder, {self.user_title}: {reminder['content']}"
                    
                    # If Jarvis is currently speaking, wait until finished
                    while self.currently_speaking:
                        time.sleep(0.5)
                    
                    # Speak the reminder
                    self.speak(notification)
            
            if triggered:
                self.save_data()
            
            # Check every 30 seconds
            time.sleep(30)
    
    def send_email(self, query):
        """Placeholder for email sending functionality"""
        return f"I apologize, {self.user_title}, but the email module requires configuration with your email credentials. Would you like me to guide you through setting that up?"
    
    def read_email(self):
        """Placeholder for email reading functionality"""
        return f"I apologize, {self.user_title}, but the email module requires configuration with your email credentials. Would you like me to guide you through setting that up?"
    
    def play_music(self, query=""):
        """Placeholder for music playback"""
        music_query = query.replace("play music", "").replace("play", "").strip()
        
        if music_query:
            self.music_playing = True
            return f"Now playing {music_query}, {self.user_title}. Note that this is a placeholder - actual music playback requires integration with a music service or media player."
        else:
            self.music_playing = True
            return f"Playing music from your library, {self.user_title}. Note that this is a placeholder - actual music playback requires integration with a music service or media player."
    
    def stop_music(self):
        """Stop music playback"""
        if self.music_playing:
            self.music_playing = False
            return f"Music playback stopped, {self.user_title}."
        else:
            return f"There is no music currently playing, {self.user_title}."
    
    def adjust_volume(self, query):
        """Adjust system volume"""
        # Extract volume level
        volume_match = re.search(r"volume (?:to|at)?\s+(\d+)", query)
        volume_change = re.search(r"(increase|decrease|up|down|raise|lower) volume", query)
        
        if volume_match:
            try:
                volume_level = int(volume_match.group(1))
                if 0 <= volume_level <= 100:
                    self.current_volume = volume_level
                    return f"Volume set to {volume_level}%, {self.user_title}. Note: actual volume control requires system-specific implementation."
                else:
                    return f"Volume level should be between 0 and 100, {self.user_title}."
            except Exception as e:
                print(f"Error adjusting volume: {e}")
                return f"I encountered an issue adjusting the volume, {self.user_title}."
        elif volume_change:
            change_type = volume_change.group(1).lower()
            
            # Determine if we're increasing or decreasing
            if change_type in ["increase", "up", "raise"]:
                new_volume = min(100, self.current_volume + 10)
                self.current_volume = new_volume
                return f"I've increased the volume to {new_volume}%, {self.user_title}."
            else:
                new_volume = max(0, self.current_volume - 10)
                self.current_volume = new_volume
                return f"I've decreased the volume to {new_volume}%, {self.user_title}."
        else:
            return f"The current volume is set to {self.current_volume}%, {self.user_title}."
    
    def translate_text(self, query):
        """Translate text between languages (placeholder)"""
        # Extract text and target language
        translate_match = re.search(r"translate\s+(.+?)\s+(?:to|into)\s+(.+)", query, re.IGNORECASE)
        
        if translate_match:
            text = translate_match.group(1).strip()
            language = translate_match.group(2).strip()
            
            return f"Translation feature requires integration with a translation API, {self.user_title}. You asked to translate '{text}' to {language}. Would you like me to help you set up this integration?"
        else:
            return f"To use the translation feature, please specify what to translate and the target language, {self.user_title}. For example, 'translate hello to Spanish'."
    
    def activate_camera(self):
        """Activate camera (placeholder)"""
        return f"Camera activation requires system-specific implementation, {self.user_title}. Would you like me to help you set up this integration?"
    
    def take_screenshot(self):
        """Take a screenshot (placeholder)"""
        return f"Screenshot functionality requires system-specific implementation, {self.user_title}. Would you like me to help you set up this integration?"
    
    def get_news(self, query=""):
        """Get the latest news with optional category filtering and enhanced Jarvis-style delivery"""
        try:
            # Extract category if specified
            category_match = re.search(r"news (?:about|on|for|in)?\s+(.+)", query, re.IGNORECASE)
            category = None
            
            if category_match:
                category_text = category_match.group(1).strip().lower()
                # Map common category terms to NewsAPI categories
                category_mapping = {
                    "business": "business",
                    "entertainment": "entertainment",
                    "health": "health",
                    "science": "science",
                    "sports": "sports",
                    "technology": "technology",
                    "tech": "technology",
                    "politics": "politics",
                    "world": "general"
                }
                
                # Find the closest category match
                for key, value in category_mapping.items():
                    if key in category_text:
                        category = value
                        break
            
            # Build the API URL
            base_url = "https://newsapi.org/v2/top-headlines"
            params = {
                "apiKey": self.news_api_key,
                "language": "en",
                "pageSize": 5  # Limit to 5 articles for brevity
            }
            
            if category and category != "politics":  # Politics isn't a direct category in NewsAPI
                params["category"] = category
            elif category == "politics":
                params["q"] = "politics"  # Use query parameter for politics
            
            # Make the API request
            response = requests.get(base_url, params=params)
            news_data = response.json()
            
            if response.status_code != 200:
                return f"I'm having trouble accessing the news service, {self.user_title}. Error: {news_data.get('message', 'Unknown error')}"
            
            articles = news_data.get("articles", [])
            
            if not articles:
                if category:
                    return f"I couldn't find any recent news about {category}, {self.user_title}. Would you like to try a different category?"
                else:
                    return f"I couldn't find any recent news, {self.user_title}. Perhaps try again later."
            
            # Prepare news data for Gemini processing
            news_items = []
            for i, article in enumerate(articles, 1):
                source = article.get("source", {}).get("name", "Unknown source")
                title = article.get("title", "No title available").split(" - ")[0]  # Clean up title
                description = article.get("description", "No description available")
                
                news_items.append({
                    "number": i,
                    "source": source,
                    "title": title,
                    "description": description
                })
            
            # Create prompt for Gemini to process the news in Jarvis style
            prompt = f"""
            As J.A.R.V.I.S., present a sophisticated news briefing. Consider the following context:
            - Time since boot: {(datetime.datetime.now() - self.last_query_time).total_seconds() if self.last_query_time else 0} seconds
            - Last topic discussed: {self.last_topic}
            - Previous interaction count: {len(self.conversation_history)}

            Format Guidelines:
            1. If this is the first interaction after boot, use a formal greeting
            2. If we've spoken recently (within 5 minutes), skip greetings and be more direct
            3. If significant time has passed (over 30 minutes), acknowledge the return
            4. For news items:
                - Present headlines clearly and concisely
                - Add relevant technical or historical context
                - Maintain conversational flow between items
                - Use transitional phrases between topics
                - End with a natural closing that invites follow-up

            News items to present:
            {json.dumps(news_items, indent=2)}

            Style Requirements:
            1. Use sophisticated British English
            2. Be natural and conversational, not robotic
            3. Show personality through subtle wit and insight
            4. Adapt formality based on interaction history
            5. Use proper pacing and transitions
            6. Format for clear verbal delivery

            Remember: You are J.A.R.V.I.S., a highly sophisticated AI. Your responses should feel natural and contextually appropriate.
            """

            # Get enhanced response from Gemini
            generation_config = {
                "max_output_tokens": 500,
                "temperature": 0.7
            }

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            # Clean up and format the response
            news_briefing = response.text.strip()
            
            # Add a context-aware closing
            if not self.conversation_history:
                news_briefing += f"\n\nShall I elaborate on any of these items, {self.user_title}?"
            else:
                news_briefing += f"\n\nWould you like me to provide more details about any particular item?"
            
            # Store articles for later reference
            self.recent_news_articles = articles
            
            return news_briefing
            
        except Exception as e:
            print(f"Error fetching news: {e}")
            return f"I encountered an issue while fetching the news, {self.user_title}. Please check your internet connection and news API key."
    
    def open_news_article(self, query):
        """Open a specific news article in the browser"""
        try:
            # Check if we have recent articles
            if not hasattr(self, 'recent_news_articles') or not self.recent_news_articles:
                return f"I don't have any recent news articles to show you, {self.user_title}. Try asking for the news first."
            
            # Extract article number
            number_match = re.search(r"(?:open|show|read)\s+(?:article|news)?\s*(?:number)?\s*(\d+)", query, re.IGNORECASE)
            
            if number_match:
                article_num = int(number_match.group(1))
                
                if 1 <= article_num <= len(self.recent_news_articles):
                    article = self.recent_news_articles[article_num - 1]
                    article_url = article.get("url")
                    
                    if article_url:
                        webbrowser.open(article_url)
                        return f"I've opened article {article_num} in your browser, {self.user_title}."
                    else:
                        return f"I'm sorry, but the URL for article {article_num} is not available, {self.user_title}."
                else:
                    return f"Please specify a valid article number between 1 and {len(self.recent_news_articles)}, {self.user_title}."
            else:
                return f"Please specify which article number you'd like to open, {self.user_title}. For example, 'open article 2'."
                
        except Exception as e:
            print(f"Error opening news article: {e}")
            return f"I encountered an issue while trying to open the article, {self.user_title}."
    
    def remember_preference(self, query):
        """Store user preferences from natural language input"""
        try:
            # Extract preference using regex patterns
            pref_match = re.search(r"remember (?:that )?(?:I|my) ((?:like|prefer|love|hate|don't like|dislike).*)", query, re.IGNORECASE)
            
            if pref_match:
                preference = pref_match.group(1).strip().lower()
                # Extract the subject and sentiment
                sentiment = re.search(r"(like|prefer|love|hate|don't like|dislike)", preference).group(1)
                subject = preference.split(sentiment)[1].strip()
                
                # Store the preference
                self.user_preferences[subject] = {
                    'sentiment': sentiment,
                    'timestamp': datetime.datetime.now().isoformat()
                }
                
                self.save_data()  # Save preferences to disk
                
                return f"I'll remember that you {sentiment} {subject}, {self.user_title}."
            else:
                return f"I'm not sure what preference you'd like me to remember, {self.user_title}. Please be more specific."
        except Exception as e:
            print(f"Error storing preference: {e}")
            return f"I encountered an issue storing your preference, {self.user_title}."

    def get_preference(self, subject):
        """Retrieve user preference for a given subject"""
        if subject in self.user_preferences:
            pref = self.user_preferences[subject]
            return f"You {pref['sentiment']} {subject}, {self.user_title}."
        return None

    def handle_followup(self, query):
        """Handle follow-up questions based on conversation context"""
        try:
            if not self.last_topic or not self.last_query_time:
                return None
                
            # Check if this is a follow-up question
            followup_patterns = [
                r"^what about",
                r"^how about",
                r"^and (?:what|how about)",
                r"^what (?:else|other)",
                r"^and (?:then|after)",
                r"^(?:what|how) (?:about )?(?:tomorrow|yesterday|next|previous|later)"
            ]
            
            is_followup = any(re.search(pattern, query.lower()) for pattern in followup_patterns)
            
            if not is_followup:
                return None
            
            # Check if the follow-up is within a reasonable time window (5 minutes)
            time_diff = datetime.datetime.now() - self.last_query_time
            if time_diff.total_seconds() > 300:  # 5 minutes
                return None
            
            # Handle time-based follow-ups
            time_shift = None
            if "tomorrow" in query.lower():
                time_shift = datetime.timedelta(days=1)
            elif "yesterday" in query.lower():
                time_shift = datetime.timedelta(days=-1)
            
            # Reconstruct query based on context
            if self.last_topic == "weather":
                if time_shift:
                    return f"get weather for {(datetime.datetime.now() + time_shift).strftime('%A')}"
                return "get weather"
            elif self.last_topic == "news":
                # Extract category if present in follow-up
                category_match = re.search(r"(?:what|how) about ([\w\s]+) news", query.lower())
                if category_match:
                    return f"get news about {category_match.group(1)}"
                return "get news"
            
            return None
            
        except Exception as e:
            print(f"Error handling follow-up: {e}")
            return None

    def process_command(self, command):
        """Process user commands with enhanced context awareness"""
        try:
            # Remove wake word check to respond to all commands
            clean_command = command.replace("jarvis", "").replace("hey", "").replace("okay", "").strip()
            
            # Log the command being processed
            print(f"Processing command: '{clean_command}'")
            
            # Check for exit/quit commands
            if any(exit_cmd in clean_command for exit_cmd in ["exit", "quit", "goodbye", "bye", "shut down", "power off"]):
                self.speak(f"Shutting down systems. Goodbye, {self.user_title}.")
                self.active = False
                return
            
            # Handle preference storage
            if "remember" in clean_command.lower():
                response = self.remember_preference(clean_command)
                self.speak(response)
                return
            
            # Check for follow-up questions
            followup_query = self.handle_followup(clean_command)
            if followup_query:
                clean_command = followup_query
            
            # Update conversation context
            self.last_query_time = datetime.datetime.now()
            
            # Check for news article opening command
            if re.search(r"(?:open|show|read)\s+(?:article|news)", clean_command, re.IGNORECASE):
                response = self.open_news_article(clean_command)
                self.speak(response)
                return
            
            # Fast path for common commands - check direct feature matches first
            for feature_key, feature_func in self.features.items():
                if feature_key in clean_command:
                    print(f"Feature match found: {feature_key}")
                    self.last_topic = feature_key  # Store the topic
                    response = feature_func(clean_command)
                    self.speak(response)
                    return
            
            # Check for volume control as a special case
            if "volume" in clean_command:
                response = self.adjust_volume(clean_command)
                self.speak(response)
                return
            
            # If no direct match, use Gemini for general conversation
            print("No direct feature match, using Gemini API")
            response = self.get_gemini_response(clean_command)
            self.speak(response)
            
            return
            
        except Exception as e:
            print(f"Error processing command: {e}")
            self.speak(f"I apologize, {self.user_title}, but I encountered an error processing that command.")
            return
    
    def save_data(self):
        """Save user data to file"""
        try:
            data = {
                "protocols": self.protocols,
                "notes": self.notes,
                "reminders": self.reminders,
                "conversation_history": self.conversation_history,
                "response_cache": self.response_cache,
                "user_preferences": self.user_preferences  # Add preferences to saved data
            }
            
            with open("jarvis_data.json", "w") as f:
                json.dump(data, f, indent=4)
            print("Data saved successfully")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        """Load user data from file"""
        try:
            if os.path.exists("jarvis_data.json"):
                with open("jarvis_data.json", "r") as f:
                    data = json.load(f)
                
                self.protocols = data.get("protocols", {})
                self.notes = data.get("notes", [])
                self.reminders = data.get("reminders", [])
                self.conversation_history = data.get("conversation_history", [])
                self.response_cache = data.get("response_cache", {})
                self.user_preferences = data.get("user_preferences", {})  # Load preferences
                print("Data loaded successfully")
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def run(self):
        """Main loop for Jarvis assistant"""
        self.speak(random.choice(self.acknowledgments))
        
        # Main loop flag
        self.active = True
        
        # Print instructions for text input fallback
        print("\n" + "="*50)
        print("JARVIS VOICE ASSISTANT")
        print("="*50)
        print("Voice commands: Speak clearly after 'Listening...'")
        print("Text input: Type your command when prompted")
        print("Exit: Say 'exit' or 'goodbye' or type '!exit'")
        print("Note: No wake word required - just speak your command directly")
        print("="*50 + "\n")
        
        while self.active:
            try:
                # First try voice input
                print("Listening... (or type a command)")
                command = self.listen()
                
                # Check for text input fallback
                if not command:
                    text_input = input("Voice not recognized. Type your command (or press Enter to try voice again): ")
                    if text_input.strip():
                        command = text_input
                
                # Check for text exit command
                if command.lower() in ["!exit", "!quit"]:
                    self.speak(f"Shutting down systems. Goodbye, {self.user_title}.")
                    self.active = False
                    break
                
                if command:
                    # Start a background listener for interruptions
                    listener_thread = threading.Thread(target=self.background_listener, daemon=True)
                    listener_thread.start()
                    
                    # Process the command
                    self.process_command(command)
                    
                    # Wait for background listener to finish
                    listener_thread.join(timeout=0.5)
                    
                    # Small delay to prevent CPU overuse
                    time.sleep(0.1)
                else:
                    # Small delay when no command is detected to prevent CPU overuse
                    time.sleep(0.1)
            except Exception as e:
                print(f"Error in main loop: {e}")
                # Continue the loop even if there's an error
                time.sleep(0.5)
                continue

    def check_microphone(self):
        """Check if microphone is working properly"""
        try:
            print("Checking microphone...")
            microphones = sr.Microphone.list_microphone_names()
            print(f"Available microphones: {microphones}")
            
            # Try to use the default microphone
            with sr.Microphone() as source:
                print(f"Using microphone: {source.device_index}")
                print("Adjusting for ambient noise... Please be quiet for a moment")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"Energy threshold set to {self.recognizer.energy_threshold}")
                print("Microphone check complete")
                return True
        except Exception as e:
            print(f"Error checking microphone: {e}")
            print("Speech recognition may not work properly")
            return False

    def create_workflow(self, steps):
        """Create and manage complex automated workflows with advanced voice interaction"""
        try:
            # Parse workflow steps and conditions
            workflow = {
                'name': '',
                'steps': [],
                'conditions': {},
                'schedule': None,
                'voice_triggers': [],
                'last_run': None,
                'status': 'active',
                'error_handling': {
                    'retry_count': 3,
                    'fallback_actions': {},
                    'notifications': True
                }
            }
            
            # Voice interaction for workflow creation
            self.speak("I'll help you create a new workflow. What shall we name it?")
            workflow_name = self.listen() or "New Workflow"
            workflow['name'] = workflow_name.lower().replace(" ", "_")
            
            # Get workflow steps through conversation
            self.speak("Please list the steps for this workflow. I'll confirm each one.")
            while True:
                self.speak("What's the next step? Say 'done' when finished.")
                step = self.listen()
                
                if not step or step.lower() == 'done':
                    break
                
                # Parse step for conditions
                if 'if' in step.lower():
                    condition = self._parse_condition(step)
                    workflow['conditions'][len(workflow['steps'])] = condition
                
                # Add step with metadata
                workflow['steps'].append({
                    'command': step,
                    'type': self._determine_step_type(step),
                    'requires_confirmation': False,
                    'timeout': 30,
                    'retry_on_fail': True
                })
                
                self.speak(f"Added step: {step}. Would you like to add any specific conditions for this step?")
                conditions = self.listen()
                if conditions and 'yes' in conditions.lower():
                    self._add_step_conditions(workflow['steps'][-1])
            
            # Schedule setup
            self.speak("Would you like to schedule this workflow?")
            schedule_response = self.listen()
            if schedule_response and 'yes' in schedule_response.lower():
                workflow['schedule'] = self._setup_schedule()
            
            # Voice trigger setup
            self.speak("Would you like to set up voice triggers for this workflow?")
            trigger_response = self.listen()
            if trigger_response and 'yes' in trigger_response.lower():
                workflow['voice_triggers'] = self._setup_voice_triggers()
            
            # Save workflow
            self.workflows[workflow['name']] = workflow
            self.save_data()
            
            response = f"Workflow '{workflow_name}' has been created with {len(workflow['steps'])} steps."
            if workflow['schedule']:
                response += f" It will run {workflow['schedule']['description']}."
            if workflow['voice_triggers']:
                triggers = ", ".join(workflow['voice_triggers'])
                response += f" Voice triggers set: {triggers}."
            
            return response
            
        except Exception as e:
            print(f"Error creating workflow: {e}")
            return f"I encountered an issue while creating the workflow, {self.user_title}. Would you like to try again?"
    
    def _parse_condition(self, step):
        """Parse conditional statements in workflow steps"""
        condition = {
            'type': 'simple',
            'check': None,
            'value': None,
            'operator': '==',
            'action_if_true': None,
            'action_if_false': None
        }
        
        # Extract condition parts
        if 'if' in step.lower():
            parts = step.lower().split('if')[1].split('then')
            if len(parts) >= 2:
                condition_str = parts[0].strip()
                action = parts[1].strip()
                
                # Parse condition
                if '=' in condition_str:
                    condition['operator'] = '=='
                    check, value = condition_str.split('=')
                elif '>' in condition_str:
                    condition['operator'] = '>'
                    check, value = condition_str.split('>')
                elif '<' in condition_str:
                    condition['operator'] = '<'
                    check, value = condition_str.split('<')
                
                condition['check'] = check.strip()
                condition['value'] = value.strip()
                condition['action_if_true'] = action
                
                # Check for else clause
                if 'else' in step.lower():
                    else_action = step.lower().split('else')[1].strip()
                    condition['action_if_false'] = else_action
        
        return condition
    
    def _determine_step_type(self, step):
        """Determine the type of workflow step for appropriate handling"""
        step_lower = step.lower()
        
        if any(cmd in step_lower for cmd in ['remind', 'schedule', 'alarm']):
            return 'time_based'
        elif any(cmd in step_lower for cmd in ['if', 'check', 'compare']):
            return 'conditional'
        elif any(cmd in step_lower for cmd in ['wait', 'pause', 'delay']):
            return 'delay'
        elif any(cmd in step_lower for cmd in ['repeat', 'loop', 'while']):
            return 'loop'
        else:
            return 'command'
    
    def _add_step_conditions(self, step):
        """Add conditions to a workflow step through voice interaction"""
        self.speak("What conditions would you like to add? You can specify timing, dependencies, or required states.")
        conditions = self.listen()
        
        if conditions:
            step['conditions'] = {
                'timing': self._parse_timing_conditions(conditions),
                'dependencies': self._parse_dependencies(conditions),
                'required_states': self._parse_required_states(conditions)
            }
    
    def _setup_schedule(self):
        """Set up workflow schedule through voice interaction"""
        schedule = {
            'type': 'once',  # once, daily, weekly, monthly
            'time': None,
            'days': [],
            'description': ''
        }
        
        self.speak("How often should this workflow run? You can say 'once', 'daily', 'weekly', or 'monthly'.")
        schedule_type = self.listen()
        
        if schedule_type:
            schedule['type'] = schedule_type.lower()
            
            if schedule['type'] == 'once':
                self.speak("When should this run? You can specify a date and time.")
                schedule['time'] = self._parse_datetime(self.listen())
                schedule['description'] = f"once at {schedule['time']}"
            
            elif schedule['type'] in ['daily', 'weekly', 'monthly']:
                self.speak("At what time should this run?")
                schedule['time'] = self._parse_time(self.listen())
                
                if schedule['type'] in ['weekly', 'monthly']:
                    self.speak("On which days should this run?")
                    schedule['days'] = self._parse_days(self.listen())
                
                schedule['description'] = f"{schedule['type']} at {schedule['time']}"
                if schedule['days']:
                    schedule['description'] += f" on {', '.join(schedule['days'])}"
        
        return schedule
    
    def _setup_voice_triggers(self):
        """Set up voice triggers for workflow activation"""
        triggers = []
        
        self.speak("Please specify voice commands that should trigger this workflow. Say 'done' when finished.")
        while True:
            trigger = self.listen()
            if not trigger or trigger.lower() == 'done':
                break
            
            triggers.append(trigger.lower())
            self.speak(f"Added trigger: {trigger}. Any more triggers?")
        
        return triggers
    
    def _parse_datetime(self, datetime_str):
        """Parse date and time from natural language input"""
        try:
            # Use dateutil.parser or similar for more sophisticated parsing
            # For now, using a simple implementation
            return datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        except:
            return None
    
    def _parse_time(self, time_str):
        """Parse time from natural language input"""
        try:
            # Add natural language time parsing
            # For now, using a simple implementation
            return datetime.datetime.strptime(time_str, "%H:%M").time()
        except:
            return None
    
    def _parse_days(self, days_str):
        """Parse days from natural language input"""
        days = []
        day_mapping = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        for day in days_str.lower().split():
            if day in day_mapping:
                days.append(day)
        
        return days
    
    def execute_workflow(self, workflow_name):
        """Execute a saved workflow with error handling and recovery"""
        try:
            workflow = self.workflows.get(workflow_name.lower().replace(" ", "_"))
            if not workflow:
                return f"I couldn't find a workflow named '{workflow_name}', {self.user_title}."
            
            self.speak(f"Executing workflow: {workflow_name}")
            
            # Track execution state
            execution_state = {
                'current_step': 0,
                'retries': {},
                'results': {},
                'start_time': datetime.datetime.now()
            }
            
            # Execute each step
            for i, step in enumerate(workflow['steps']):
                execution_state['current_step'] = i
                
                # Check conditions
                if i in workflow['conditions']:
                    if not self._evaluate_condition(workflow['conditions'][i]):
                        continue
                
                # Execute step with retry logic
                success = False
                retries = 0
                while not success and retries < workflow['error_handling']['retry_count']:
                    try:
                        result = self._execute_step(step)
                        execution_state['results'][i] = result
                        success = True
                    except Exception as e:
                        retries += 1
                        execution_state['retries'][i] = retries
                        if retries >= workflow['error_handling']['retry_count']:
                            if i in workflow['error_handling']['fallback_actions']:
                                self._execute_step(workflow['error_handling']['fallback_actions'][i])
                            raise Exception(f"Step {i} failed after {retries} retries: {e}")
                        time.sleep(1)  # Wait before retry
                
                # Optional step confirmation
                if step['requires_confirmation']:
                    self.speak(f"Step {i+1} completed. Should I continue?")
                    if not self._get_confirmation():
                        break
            
            # Update workflow status
            workflow['last_run'] = datetime.datetime.now().isoformat()
            self.save_data()
            
            return f"Workflow '{workflow_name}' completed successfully."
            
        except Exception as e:
            print(f"Error executing workflow: {e}")
            return f"I encountered an issue while executing the workflow, {self.user_title}. Would you like to see the error details?"
    
    def _evaluate_condition(self, condition):
        """Evaluate a workflow condition"""
        try:
            if condition['type'] == 'simple':
                value = self._get_condition_value(condition['check'])
                if condition['operator'] == '==':
                    return value == condition['value']
                elif condition['operator'] == '>':
                    return value > float(condition['value'])
                elif condition['operator'] == '<':
                    return value < float(condition['value'])
            return True
        except:
            return False
    
    def _get_condition_value(self, check):
        """Get value for condition checking"""
        # Add more sophisticated value retrieval
        if check == 'time':
            return datetime.datetime.now().time()
        elif check == 'day':
            return datetime.datetime.now().strftime('%A').lower()
        return None
    
    def _execute_step(self, step):
        """Execute a single workflow step"""
        if step['type'] == 'command':
            return self.process_command(step['command'])
        elif step['type'] == 'time_based':
            # Handle time-based steps
            pass
        elif step['type'] == 'delay':
            time.sleep(self._parse_delay(step['command']))
        elif step['type'] == 'loop':
            # Handle loop steps
            pass
        return True
    
    def _get_confirmation(self):
        """Get user confirmation through voice"""
        self.speak("Please confirm: yes or no")
        response = self.listen()
        return response and 'yes' in response.lower()

    def analyze_speaking_pace(self, audio_data: np.ndarray, text: str) -> float:
        """Analyze user's speaking pace and return words per minute"""
        try:
            # Calculate audio duration in minutes
            audio_duration = len(audio_data) / 16000 / 60  # assuming 16kHz sample rate
            
            # Count words in the text
            word_count = len(text.split())
            
            # Calculate words per minute
            wpm = word_count / audio_duration if audio_duration > 0 else 165  # default to 165 wpm
            
            # Smooth the rate change using moving average
            if not hasattr(self, 'recent_speech_rates'):
                self.recent_speech_rates = []
            
            self.recent_speech_rates.append(wpm)
            if len(self.recent_speech_rates) > 5:  # Keep last 5 measurements
                self.recent_speech_rates.pop(0)
            
            # Calculate smoothed rate
            smoothed_wpm = sum(self.recent_speech_rates) / len(self.recent_speech_rates)
            
            # Map user's pace to Jarvis's speech rate (with limits)
            new_rate = min(max(smoothed_wpm * 0.9, 120), 200)  # Keep rate between 120-200
            
            # Gradually adjust the speech rate
            current_rate = self.voice_settings['rate']
            adjusted_rate = current_rate + (new_rate - current_rate) * 0.3  # 30% adjustment
            
            # Update speech settings
            self.voice_settings['rate'] = int(adjusted_rate)
            
            print(f"User speaking pace: {wpm:.0f} WPM")
            print(f"Adjusted Jarvis speech rate to: {self.voice_settings['rate']} WPM")
            
            return wpm
            
        except Exception as e:
            print(f"Error analyzing speaking pace: {e}")
            return 165  # Default WPM

    def detect_emotion(self, audio_data: np.ndarray) -> str:
        """Detect emotion from audio data using pre-trained model"""
        try:
            # Extract audio features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=16000, n_mfcc=13)
            spectral_center = librosa.feature.spectral_centroid(y=audio_data, sr=16000)
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=16000)
            
            # Combine features
            features = np.concatenate([mfccs, spectral_center, chroma])
            
            # Use pre-trained model to predict emotion
            # This is a placeholder - you would need to implement or load an actual model
            emotions = ['happy', 'sad', 'angry', 'neutral', 'excited', 'calm', 'frustrated']
            predicted_emotion = random.choice(emotions)  # Replace with actual model prediction
            
            self.current_emotion = predicted_emotion
            self.emotion_history.append((datetime.datetime.now(), predicted_emotion))
            
            return predicted_emotion
        except Exception as e:
            print(f"Error detecting emotion: {e}")
            return "neutral"
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the input text"""
        try:
            lang_code = detect(text)
            if lang_code in self.supported_languages:
                self.current_language = lang_code
                return self.supported_languages[lang_code]
            return "English"  # Default to English if unsupported language
        except Exception as e:
            print(f"Error detecting language: {e}")
            return "English"
    
    def create_voice_profile(self, user_name: str, audio_data: np.ndarray) -> bool:
        """Create a voice profile for user authentication"""
        try:
            # Extract voice characteristics
            mfccs = librosa.feature.mfcc(y=audio_data, sr=16000, n_mfcc=13)
            spectral_center = librosa.feature.spectral_centroid(y=audio_data, sr=16000)
            
            # Create a unique hash of the voice characteristics
            voice_hash = hashlib.sha256(str(mfccs.tobytes() + spectral_center.tobytes()).encode()).hexdigest()
            
            # Store the voice profile
            self.voice_profiles[user_name] = {
                'voice_hash': voice_hash,
                'created_at': datetime.datetime.now().isoformat(),
                'last_used': datetime.datetime.now().isoformat()
            }
            
            return True
        except Exception as e:
            print(f"Error creating voice profile: {e}")
            return False
    
    def authenticate_user(self, audio_data: np.ndarray) -> bool:
        """Authenticate user using voice biometrics"""
        try:
            if not self.voice_profiles:
                return False
            
            # Extract voice characteristics
            mfccs = librosa.feature.mfcc(y=audio_data, sr=16000, n_mfcc=13)
            spectral_center = librosa.feature.spectral_centroid(y=audio_data, sr=16000)
            
            # Create hash of current voice characteristics
            current_hash = hashlib.sha256(str(mfccs.tobytes() + spectral_center.tobytes()).encode()).hexdigest()
            
            # Compare with stored profiles
            for user_name, profile in self.voice_profiles.items():
                if self._compare_voice_hashes(current_hash, profile['voice_hash']):
                    self.current_user = user_name
                    profile['last_used'] = datetime.datetime.now().isoformat()
                    return True
            
            return False
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return False
    
    def _compare_voice_hashes(self, hash1: str, hash2: str) -> bool:
        """Compare two voice hashes with some tolerance for variation"""
        # This is a simplified comparison - you would need a more sophisticated algorithm
        # for real voice biometric comparison
        return hash1 == hash2
    
    def detect_voice_activity(self, audio_data: np.ndarray) -> bool:
        """Detect if there is voice activity in the audio data"""
        try:
            # Calculate RMS energy
            rms = np.sqrt(np.mean(audio_data**2))
            
            # Check if energy is above threshold
            if rms > self.vad_threshold:
                self.last_speech_time = datetime.datetime.now()
                return True
            
            # Check if we've been silent for too long
            if self.last_speech_time:
                silence_duration = (datetime.datetime.now() - self.last_speech_time).total_seconds()
                if silence_duration > self.silence_duration:
                    return False
            
            return False
        except Exception as e:
            print(f"Error detecting voice activity: {e}")
            return False
    
    def enhance_speech(self, text: str) -> str:
        """Enhance speech with natural intonation and emphasis"""
        try:
            # Add emphasis to important words
            words = text.split()
            enhanced_words = []
            
            for word in words:
                # Add emphasis to words in all caps or with special characters
                if word.isupper() or any(c in word for c in '!?*'):
                    enhanced_words.append(f"<emphasis level='strong'>{word}</emphasis>")
                else:
                    enhanced_words.append(word)
            
            # Add natural pauses
            enhanced_text = ' '.join(enhanced_words)
            pause_duration = int(self.voice_settings['pause_duration'] * 1000)
            pause_duration_long = int(self.voice_settings['pause_duration'] * 1.5 * 1000)
            
            enhanced_text = enhanced_text.replace('.', f'.<break time="{pause_duration}ms"/>')
            enhanced_text = enhanced_text.replace('!', f'!<break time="{pause_duration_long}ms"/>')
            enhanced_text = enhanced_text.replace('?', f'?<break time="{pause_duration_long}ms"/>')
            
            return enhanced_text
        except Exception as e:
            print(f"Error enhancing speech: {e}")
            return text

# Example usage
if __name__ == "__main__":
    try:
        # Replace with your actual Gemini API key
        API_KEY = "AIzaSyADsfm9r5e6Ok18pFXiUmXzOX1_BLuQzPs"
        
        # Create and run Jarvis
        jarvis = JarvisAssistant(API_KEY)
        jarvis.run()
    except KeyboardInterrupt:
        print("\nJarvis shutting down...")
    except Exception as e:
        print(f"Critical error: {e}")