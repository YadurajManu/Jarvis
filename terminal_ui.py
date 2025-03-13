from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.align import Align
from rich import box
import time
import threading
import itertools
import datetime

class TerminalUI:
    def __init__(self):
        """Initialize the terminal UI with Rich console"""
        self.console = Console()
        self.animation_active = False
        self.spinner_styles = ["dots", "dots2", "dots3", "dots4", "arc", "star"]
        self.current_spinner = 0

    def display_boot_sequence(self):
        """Display an animated boot sequence"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            # Initialize systems task
            init_task = progress.add_task("[cyan]Initializing J.A.R.V.I.S. systems...", total=100)
            for i in range(101):
                progress.update(init_task, completed=i)
                time.sleep(0.02)

            # Load modules task
            modules_task = progress.add_task("[green]Loading core modules...", total=100)
            for i in range(101):
                progress.update(modules_task, completed=i)
                time.sleep(0.01)

            # Configure settings task
            settings_task = progress.add_task("[yellow]Configuring system settings...", total=100)
            for i in range(101):
                progress.update(settings_task, completed=i)
                time.sleep(0.015)

        # Display welcome message
        self.console.print("\n[bold cyan]J.A.R.V.I.S.[/bold cyan] [green]Online[/green]")
        self.console.print("[dim]All systems operational[/dim]\n")

    def display_speech(self, text, user=False):
        """Display speech in a styled panel"""
        style = "yellow" if user else "cyan"
        speaker = "You" if user else "JARVIS"
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        
        panel = Panel(
            Text(text, style=style),
            title=f"[{current_time}] {speaker}",
            border_style=style,
            box=box.ROUNDED
        )
        self.console.print(panel)

    def display_error(self, message):
        """Display error messages in a red panel"""
        panel = Panel(
            Text(message, style="red"),
            title="Error",
            border_style="red",
            box=box.HEAVY
        )
        self.console.print(panel)

    def display_system_info(self, cpu_usage, memory_info, ip):
        """Display system information in a formatted table"""
        table = Table(title="System Information", box=box.DOUBLE)
        
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("CPU Usage", f"{cpu_usage}%")
        table.add_row("Memory Total", f"{memory_info['total']:.2f} GB")
        table.add_row("Memory Used", f"{memory_info['used']:.2f} GB")
        table.add_row("Memory Usage", f"{memory_info['percent']}%")
        table.add_row("IP Address", ip)
        
        self.console.print(table)

    def display_news(self, articles):
        """Display news articles in a formatted table"""
        table = Table(title="Latest News", box=box.DOUBLE)
        
        table.add_column("#", style="cyan", width=4)
        table.add_column("Title", style="green")
        table.add_column("Source", style="yellow", width=20)
        table.add_column("Published", style="blue", width=20)
        
        for idx, article in enumerate(articles, 1):
            table.add_row(
                str(idx),
                article.get('title', 'N/A'),
                article.get('source', {}).get('name', 'Unknown'),
                article.get('publishedAt', 'N/A')[:10]
            )
        
        self.console.print(table)

    def display_help(self):
        """Display available commands and features"""
        help_text = """
        [bold cyan]Available Commands:[/bold cyan]
        
        [yellow]Basic Commands:[/yellow]
        • "time" - Get current time
        • "date" - Get current date
        • "weather" - Get weather information
        • "news" - Get latest news
        
        [yellow]System Commands:[/yellow]
        • "cpu info" - CPU usage information
        • "memory info" - Memory usage information
        • "system info" - Full system information
        
        [yellow]Utility Commands:[/yellow]
        • "search [query]" - Search the web
        • "wikipedia [topic]" - Search Wikipedia
        • "take note" - Create a note
        • "read notes" - View saved notes
        
        [yellow]Media Commands:[/yellow]
        • "play music" - Start music playback
        • "stop music" - Stop music playback
        • "volume [level]" - Adjust volume
        
        [dim]Type "exit" or "quit" to shut down J.A.R.V.I.S.[/dim]
        """
        
        panel = Panel(
            help_text,
            title="J.A.R.V.I.S. Help Guide",
            border_style="cyan",
            box=box.ROUNDED
        )
        self.console.print(panel)

    def show_listening_animation(self):
        """Show an animated listening indicator"""
        self.animation_active = True
        frames = ["🎤 ", "🎤 .", "🎤 ..", "🎤 ..."]
        
        with Live(refresh_per_second=4) as live:
            while self.animation_active:
                for frame in frames:
                    if not self.animation_active:
                        break
                    live.update(Text(frame, style="cyan"))
                    yield
                    time.sleep(0.25)

    def show_processing_animation(self, message="Processing"):
        """Show an animated processing indicator"""
        self.animation_active = True
        spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        
        with Live(refresh_per_second=10) as live:
            while self.animation_active:
                live.update(Text(f"{next(spinner)} {message}...", style="yellow"))
                yield
                time.sleep(0.1)

    def stop_animation(self):
        """Stop any running animation"""
        self.animation_active = False

    def display_notes(self, notes):
        """Display saved notes in a table"""
        table = Table(title="Saved Notes", box=box.DOUBLE)
        
        table.add_column("Date", style="cyan")
        table.add_column("Note", style="yellow")
        
        for note in notes:
            table.add_row(
                note.get('timestamp', 'N/A'),
                note.get('content', 'Empty note')
            )
        
        self.console.print(table)

    def update_voice_activity(self, level):
        """Update voice activity visualization"""
        bars = int(level * 20)  # Scale the level to 0-20 bars
        activity = "█" * bars + "░" * (20 - bars)
        self.console.print(f"\rVoice Level: {activity}", end="")

    def update_emotion_display(self, emotion):
        """Update emotion display with corresponding emoji"""
        emotion_emojis = {
            'happy': '😊',
            'sad': '😢',
            'angry': '😠',
            'neutral': '😐',
            'excited': '😃',
            'calm': '😌',
            'frustrated': '😤'
        }
        emoji = emotion_emojis.get(emotion.lower(), '😐')
        self.console.print(f"\rDetected emotion: {emoji} {emotion}", end="") 