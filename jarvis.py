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

class JarvisAssistant:
    def __init__(self, api_key, user_name="Yaduraj"):
        # User information
        self.user_name = user_name
        self.user_title = "sir"  # Iron Man style addressing
        
        # Initialize Gemini API
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
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
            "ip": self.ip_info,
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
        """Convert text to speech with Iron Man Jarvis style and intervention support"""
        # Add short pauses for more natural speech using commas and periods
        text = text.replace(',', ', ')
        text = text.replace('.', '. ')
        text = text.replace('?', '? ')
        
        # Add some British butler-like phrases occasionally
        if random.random() < 0.1 and not text.startswith(("I'm afraid", "Unfortunately")):
            british_phrases = [
                f"If I may say so, {self.user_title}, ",
                f"I believe, {self.user_title}, that ",
                f"Might I suggest that ",
                f"If I may be so bold, {self.user_title}, ",
                f"Indeed, {self.user_title}, "
            ]
            text = random.choice(british_phrases) + text[0].lower() + text[1:]
        
        if print_output:
            print(f"JARVIS: {text}")
        
        # Break speech into chunks for better interruption handling
        chunks = re.split('(?<=[.!?]) +', text)
        
        self.currently_speaking = True
        self.interrupt_speech = False
        
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
    
    def listen(self, timeout=5, interrupt_mode=False):
        """Listen for voice commands with optional interruption mode"""
        with sr.Microphone() as source:
            if not interrupt_mode:
                print("Listening...")
            
            # Reduce the duration of ambient noise adjustment
            self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
            try:
                # Reduce timeout and phrase_time_limit for faster response
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=10)
                if not interrupt_mode:
                    print("Processing speech...")
                # Use recognize_google with shorter timeout
                text = self.recognizer.recognize_google(audio, language='en-US')
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
            
            # Only show processing message occasionally to speed up interaction
            if random.random() > 0.9:
                self.speak(random.choice(self.processing_phrases), print_output=False)
            
            # Build context from conversation history - limit to last 3 for faster processing
            context = "\n".join([f"User: {q}\nJarvis: {r}" for q, r in self.conversation_history[-3:]])
            
            # Create a more concise prompt for faster processing
            prompt = f"""
            You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), the AI assistant created by Tony Stark and serving {self.user_name}.
            
            Instructions:
            - Respond like J.A.R.V.I.S. from Iron Man movies
            - Use formal, British butler-like tone with wit
            - Address user as "sir"
            - Be concise and direct
            - Use technical terms when appropriate
            
            Recent context:
            {context}
            
            User query: {query}
            
            Respond as J.A.R.V.I.S.:
            """
            
            # Set a maximum output length and temperature for faster responses
            generation_config = {
                "max_output_tokens": 150,
                "temperature": 0.7
            }
            
            # Get response from Gemini with timeout
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Remove any "JARVIS:" prefixes that might be in the response
            cleaned_response = response.text.replace("JARVIS: ", "").strip()
            
            # Add to conversation history
            self.conversation_history.append((query, cleaned_response))
            
            # Limit history length
            if len(self.conversation_history) > 5:
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
    def get_time(self, query=None):
        """Get current time"""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        return f"The current time is {current_time}, {self.user_title}."
    
    def get_date(self, query=None):
        """Get current date"""
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {current_date}, {self.user_title}."
    
    def get_day(self, query=None):
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
    
    def open_browser(self, query=None):
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
    
    def system_info(self, query=None):
        """Get system information"""
        try:
            system = platform.system()
            processor = platform.processor()
            version = platform.version()
            
            return f"You're currently running {system} {version} on a {processor} processor, {self.user_title}."
        except:
            return f"I encountered an issue while accessing your system information, {self.user_title}."
    
    def cpu_info(self, query=None):
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
    
    def memory_info(self, query=None):
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
    
    def ip_info(self, query=None):
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
    
    def tell_joke(self, query=None):
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
    
    def read_email(self, query=None):
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
    
    def activate_camera(self, query=None):
        """Activate camera (placeholder)"""
        return f"Camera activation requires system-specific implementation, {self.user_title}. Would you like me to help you set up this integration?"
    
    def take_screenshot(self, query=None):
        """Take a screenshot (placeholder)"""
        return f"Screenshot functionality requires system-specific implementation, {self.user_title}. Would you like me to help you set up this integration?"
    
    def process_command(self, command):
        """Process user commands and determine appropriate action"""
        try:
            # Remove wake word check to respond to all commands
            # Just clean the command in case wake words are still used out of habit
            clean_command = command.replace("jarvis", "").replace("hey", "").replace("okay", "").strip()
            
            # Log the command being processed
            print(f"Processing command: '{clean_command}'")
            
            # Check for exit/quit commands
            if any(exit_cmd in clean_command for exit_cmd in ["exit", "quit", "goodbye", "bye", "shut down", "power off"]):
                self.speak(f"Shutting down systems. Goodbye, {self.user_title}.")
                self.active = False
                return
            
            # Fast path for common commands - check direct feature matches first
            for feature_key, feature_func in self.features.items():
                if feature_key in clean_command:
                    print(f"Feature match found: {feature_key}")
                    # All functions now accept an optional parameter
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
            
            # Explicitly return to ensure we continue the main loop
            return
            
        except Exception as e:
            print(f"Error processing command: {e}")
            self.speak(f"I apologize, {self.user_title}, but I encountered an error processing that command.")
            # Don't exit the loop on error
            return
    
    def save_data(self):
        """Save user data to file"""
        try:
            data = {
                "protocols": self.protocols,
                "notes": self.notes,
                "reminders": self.reminders,
                "conversation_history": self.conversation_history,
                "response_cache": self.response_cache
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