from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.layout import Layout
from rich.syntax import Syntax
from rich import box
from art import text2art
from termcolor import colored
from tqdm import tqdm
import time
import sys
import os
import math

class JarvisUI:
    def __init__(self):
        """Initialize the UI manager with Rich console and styling"""
        self.console = Console()
        self.current_animation = None
        self.voice_activity_display = None
        
        # Voice visualization settings
        self.viz_width = 50
        self.viz_height = 3
        self.viz_chars = "▁▂▃▄▅▆▇█"
        
        # Emotion colors
        self.emotion_colors = {
            'happy': 'green',
            'sad': 'blue',
            'angry': 'red',
            'neutral': 'white',
            'excited': 'yellow',
            'calm': 'cyan',
            'frustrated': 'magenta'
        }
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def show_boot_sequence(self):
        """Enhanced boot sequence with animations"""
        # Clear screen first
        self.clear_screen()
        
        # Show JARVIS ASCII art
        jarvis_art = text2art("JARVIS", font='block')
        self.console.print(Panel(jarvis_art, style="bold blue"))
        
        # Initialize system with progress bars
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            # Add multiple initialization tasks
            tasks = [
                ("Initializing core systems", 2),
                ("Loading voice recognition", 1.5),
                ("Calibrating audio processors", 1),
                ("Establishing neural networks", 2),
                ("Loading user preferences", 1),
                ("Activating security protocols", 1.5),
                ("Syncing with remote servers", 2)
            ]
            
            progress_tasks = []
            for desc, duration in tasks:
                task = progress.add_task(desc, total=100)
                progress_tasks.append((task, duration))
            
            # Simulate initialization
            for _ in range(100):
                for task, duration in progress_tasks:
                    if not progress.finished:
                        progress.update(task, advance=1)
                        time.sleep(duration / 100)

    def show_listening_animation(self):
        """Enhanced listening animation with voice activity visualization"""
        layout = Layout()
        layout.split_column(
            Layout(name="status"),
            Layout(name="visualization")
        )
        
        with Live(layout, refresh_per_second=10) as live:
            while True:
                # Update status
                layout["status"].update(Panel("🎤 Listening...", style="bold green"))
                
                # Update visualization
                if hasattr(self, 'current_voice_level'):
                    viz = self.create_voice_visualization(self.current_voice_level)
                    layout["visualization"].update(Panel(viz, style="blue"))
                
                yield
                time.sleep(0.1)

    def create_voice_visualization(self, level):
        """Create a real-time voice activity visualization"""
        # Normalize level to 0-1
        normalized_level = min(1.0, level / 0.5)
        
        # Create visualization bars
        bars = []
        for i in range(self.viz_width):
            # Create a wave pattern
            value = normalized_level * math.sin(time.time() * 10 + i * 0.2)
            value = abs(value)  # Take absolute value for positive bars
            
            # Map value to visualization characters
            char_index = int(value * (len(self.viz_chars) - 1))
            bars.append(self.viz_chars[char_index])
        
        return '\n'.join([''.join(bars)] * self.viz_height)

    def update_voice_activity(self, level):
        """Update the voice activity visualization"""
        self.current_voice_level = level

    def update_emotion_display(self, emotion):
        """Update the emotion display in real-time"""
        color = self.emotion_colors.get(emotion, 'white')
        emotion_text = f"😊 {emotion.capitalize()}" if emotion == 'happy' else \
                      f"😢 {emotion.capitalize()}" if emotion == 'sad' else \
                      f"😠 {emotion.capitalize()}" if emotion == 'angry' else \
                      f"😐 {emotion.capitalize()}" if emotion == 'neutral' else \
                      f"🎉 {emotion.capitalize()}" if emotion == 'excited' else \
                      f"😌 {emotion.capitalize()}" if emotion == 'calm' else \
                      f"😤 {emotion.capitalize()}"
        
        self.console.print(Panel(emotion_text, style=f"bold {color}"))

    def show_processing_animation(self, message="Processing"):
        """Show processing animation with message"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(message, total=None)
            while True:
                yield
                time.sleep(0.1)

    def display_speech(self, text, user=False):
        """Display speech with enhanced styling"""
        style = "bold yellow" if user else "bold blue"
        prefix = "You:" if user else "JARVIS:"
        
        # Add emotion indicator if available
        emotion_indicator = ""
        if hasattr(self, 'current_emotion') and not user:
            emotion = self.current_emotion
            emotion_indicator = self.get_emotion_emoji(emotion) + " "
        
        self.console.print(Panel(f"{emotion_indicator}{text}", title=prefix, style=style))

    def get_emotion_emoji(self, emotion):
        """Get appropriate emoji for emotion"""
        emotion_emojis = {
            'happy': '😊',
            'sad': '😢',
            'angry': '😠',
            'neutral': '😐',
            'excited': '🎉',
            'calm': '😌',
            'frustrated': '😤'
        }
        return emotion_emojis.get(emotion, '')

    def display_system_info(self, cpu_usage, memory_info, ip_info):
        """Display system information in a formatted table"""
        table = Table(title="System Information", box=box.DOUBLE_EDGE)
        
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")
        
        table.add_row("CPU Usage", f"{cpu_usage}%")
        table.add_row("Memory Used", f"{memory_info['used']:.2f}GB / {memory_info['total']:.2f}GB")
        table.add_row("Memory %", f"{memory_info['percent']}%")
        table.add_row("IP Address", ip_info)
        
        self.console.print(table)
        
    def display_news(self, articles):
        """Display news articles in a formatted table"""
        table = Table(title="Latest News", box=box.DOUBLE_EDGE)
        
        table.add_column("No.", style="cyan", width=4)
        table.add_column("Headline", style="white")
        table.add_column("Source", style="green", width=20)
        
        for i, article in enumerate(articles, 1):
            table.add_row(
                str(i),
                article['title'],
                article['source']['name']
            )
            
        self.console.print(table)
        
    def display_emotion(self, emotion):
        """Display detected emotion with appropriate styling"""
        emotion_colors = {
            'happy': 'green',
            'sad': 'blue',
            'angry': 'red',
            'neutral': 'white',
            'excited': 'yellow',
            'calm': 'cyan',
            'frustrated': 'magenta'
        }
        
        color = emotion_colors.get(emotion, 'white')
        self.console.print(f"\n[{color}]Detected emotion: {emotion}[/{color}]")
        
    def display_reminder(self, reminder):
        """Display a reminder notification"""
        panel = Panel(
            reminder['content'],
            title="🔔 Reminder",
            title_align="left",
            border_style="yellow",
            box=box.ROUNDED
        )
        self.console.print(panel)
        
    def display_notes(self, notes):
        """Display notes in a formatted table"""
        table = Table(title="📝 Your Notes", box=box.DOUBLE_EDGE)
        
        table.add_column("Date", style="cyan")
        table.add_column("Content", style="white")
        
        for note in notes:
            table.add_row(
                note['timestamp'],
                note['content']
            )
            
        self.console.print(table)
        
    def display_help(self):
        """Display available commands and features"""
        help_text = """
        [bold]Available Commands:[/bold]
        
        🕒 [cyan]Time & Date[/cyan]
        • "What time is it?"
        • "What's today's date?"
        • "What day is it?"
        
        💻 [cyan]System Information[/cyan]
        • "Check CPU usage"
        • "Show memory info"
        • "What's my IP address?"
        
        🌐 [cyan]Web Interaction[/cyan]
        • "Search for [query]"
        • "Look up [topic] on Wikipedia"
        • "Open browser"
        
        📰 [cyan]News[/cyan]
        • "Get the latest news"
        • "Show me technology news"
        • "What's happening in sports?"
        
        🎙️ [cyan]Voice Features[/cyan]
        • "Create voice profile for [name]"
        • "Enable voice authentication"
        • "Switch to [language]"
        
        📝 [cyan]Notes & Reminders[/cyan]
        • "Take a note: [content]"
        • "Remind me to [task] at [time]"
        • "Show my notes"
        
        ⚡ [cyan]Advanced Features[/cyan]
        • "Define protocol [name] as [steps]"
        • "Run protocol [name]"
        • "Create workflow [name]"
        """
        
        panel = Panel(
            help_text,
            title="JARVIS Help Guide",
            border_style="blue",
            box=box.DOUBLE
        )
        self.console.print(panel)
        
    def display_error(self, error_message):
        """Display error messages"""
        panel = Panel(
            f"[red]{error_message}[/red]",
            title="⚠️ Error",
            border_style="red",
            box=box.HEAVY
        )
        self.console.print(panel)
        
    def display_success(self, message):
        """Display success messages"""
        panel = Panel(
            f"[green]{message}[/green]",
            title="✅ Success",
            border_style="green",
            box=box.HEAVY
        )
        self.console.print(panel) 