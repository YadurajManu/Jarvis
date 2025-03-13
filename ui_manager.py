from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich import box
from art import text2art
from termcolor import colored
from tqdm import tqdm
import time
import sys
import os

class JarvisUI:
    def __init__(self):
        """Initialize the UI manager with Rich console and styling"""
        self.console = Console()
        self.spinner_styles = ['dots', 'dots12', 'line', 'arrow3', 'bouncingBar', 'clock']
        self.current_spinner = 0
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def show_boot_sequence(self):
        """Display an animated boot sequence"""
        self.clear_screen()
        
        # Show JARVIS ASCII art
        jarvis_art = text2art("J.A.R.V.I.S", font="block")
        self.console.print(f"[bold blue]{jarvis_art}[/bold blue]")
        
        # Initialize systems with progress bars
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            
            tasks = [
                ("Initializing core systems...", 2),
                ("Loading voice recognition modules...", 1.5),
                ("Calibrating audio interfaces...", 1),
                ("Establishing neural networks...", 2),
                ("Loading language models...", 1.5),
                ("Configuring security protocols...", 1),
                ("Optimizing response algorithms...", 1.5)
            ]
            
            for desc, duration in tasks:
                task = progress.add_task(desc, total=None)
                time.sleep(duration)
                progress.remove_task(task)
                
        self.console.print("\n[bold green]All systems operational[/bold green]")
        time.sleep(1)
        
    def show_listening_animation(self):
        """Display an animated listening indicator"""
        with Progress(
            SpinnerColumn(spinner_name="dots12"),
            TextColumn("[bold blue]Listening...[/bold blue]"),
            console=self.console,
            transient=True
        ) as progress:
            progress.add_task("", total=None)
            while True:
                yield
                
    def show_processing_animation(self, task="Processing"):
        """Display an animated processing indicator"""
        with Progress(
            SpinnerColumn(spinner_name="line"),
            TextColumn(f"[bold yellow]{task}...[/bold yellow]"),
            console=self.console,
            transient=True
        ) as progress:
            progress.add_task("", total=None)
            while True:
                yield
                
    def display_speech(self, text, user=False):
        """Display speech in a stylized panel"""
        style = "bold green" if user else "bold blue"
        speaker = "You" if user else "JARVIS"
        
        panel = Panel(
            text,
            title=speaker,
            title_align="left",
            border_style=style,
            box=box.ROUNDED
        )
        self.console.print(panel)
        
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