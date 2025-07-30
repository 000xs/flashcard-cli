import typer
from rich.console import Console
from rich.prompt import Prompt
from flashcard_cli.data import load_flashcards, save_flashcard

app = typer.Typer()
console = Console()

@app.command()
def add():
    """
    Adds a new flashcard. flashcard add command
    """
    question = Prompt.ask("Enter the question")
    answer = Prompt.ask("Enter the answer")

    save_flashcard(question, answer)
    console.print("[bold green]Flashcard added![/bold green]")

@app.command()
def start():
    """
    Starts the flashcard learning session.
    """
    from flashcard_cli.start import start_flashcards
    start_flashcards()

# flashcard mannage commands
@app.command()
def manage():
    """
    Flash Cards Edit And Delete Commands with terminal UI
        - Show Screen Listed with id all card as table
        - can use updown arow ans switch eac and when select item (card)
        - selected card and press 'e' can edit and press 'del' can delete falshcard
        - screen had header contet centr and footer
        - header include appname date like basic data
        - center add selct  listed cards
        - footer include key guide
    """
    from flashcard_cli.tui import FlashcardApp
    app = FlashcardApp()
    app.run()
   

def main():
    app()

if __name__ == "__main__":
    main()
