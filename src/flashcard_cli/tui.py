from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Input, Button, Static, ProgressBar
from textual.containers import Vertical, Center
from textual.screen import Screen
from textual.binding import Binding
from textual.widgets import Label

from flashcard_cli.data import con, load_flashcards
from flashcard_cli.db import delete_flashcard, edit_card

class EditScreen(Screen):
    """Screen for editing a flashcard."""

    def __init__(self, card_id: int, question: str, answer: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.card_id = card_id
        self.question = question
        self.answer = answer

    def compose(self) -> ComposeResult:
        yield Vertical(
            Input(self.question, id="question"),
            Input(self.answer, id="answer"),
            Button("Save", variant="primary", id="save"),
            Button("Cancel", id="cancel"),
            id="edit_dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            new_question = self.query_one("#question", Input).value
            new_answer = self.query_one("#answer", Input).value
            self.dismiss((self.card_id, new_question, new_answer))
        else:
            self.dismiss()


class FlashcardApp(App):
    """A Textual app to manage flashcards."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("e", "edit_card", "Edit"),
        Binding("d", "delete_card", "Delete"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flashcards = load_flashcards()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield DataTable(id="flashcard_table")
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.update_table()

    def update_table(self):
        """Reloads the flashcards and updates the DataTable."""
        self.flashcards = load_flashcards()
        table = self.query_one("#flashcard_table", DataTable)
        table.clear()
        table.add_columns("ID", "Question", "Answer")
        for card in self.flashcards:
            table.add_row(str(card["id"]), card["question"], card["answer"])

    def action_quit(self) -> None:
        """An action to quit the app."""
        self.exit()

    def action_edit_card(self) -> None:
        """An action to edit the selected card."""
        table = self.query_one(DataTable)
        if table.cursor_row >= 0:
            row_key = table.get_row_at(table.cursor_row)[0]
            card_id = int(row_key)
            
            card = next((c for c in self.flashcards if c["id"] == card_id), None)

            if card:
                def update_card(result):
                    if result:
                        card_id, new_question, new_answer = result
                        edit_card(con, card_id, new_question, new_answer)
                        self.update_table()

                self.push_screen(EditScreen(card_id, card["question"], card["answer"]), update_card)

    def action_delete_card(self) -> None:
        """An action to delete the selected card."""
        table = self.query_one(DataTable)
        if table.cursor_row >= 0:
            row_key = table.get_row_at(table.cursor_row)[0]
            card_id = int(row_key)
            delete_flashcard(con, card_id)
            self.update_table()

class AnswerScreen(Screen):
    """Screen to display the answer in a popup."""
    def __init__(self, answer: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.answer = answer

    def compose(self) -> ComposeResult:
        yield Center(
            Vertical(
                Label("Answer"),
                Static(self.answer, id="answer_text"),
                Button("OK", variant="primary", id="ok_button"),
                id="answer_dialog",
            )
        )

    def on_mount(self) -> None:
        self.query_one("#answer_dialog").styles.border = ("heavy", "green")
        self.query_one("#answer_dialog").styles.width = "60%"
        self.query_one("#answer_dialog").styles.height = "auto"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

class CorrectnessScreen(Screen):
    """Screen to ask the user if they were correct."""
    def compose(self) -> ComposeResult:
        yield Center(
            Vertical(
                Label("Did you get it right?"),
                Button("Yes", variant="success", id="yes_button"),
                Button("No", variant="error", id="no_button"),
                id="correctness_dialog",
            )
        )

    def on_mount(self) -> None:
        self.query_one("#correctness_dialog").styles.border = ("heavy", "white")
        self.query_one("#correctness_dialog").styles.width = "40%"
        self.query_one("#correctness_dialog").styles.height = "auto"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes_button":
            self.dismiss(True)
        else:
            self.dismiss(False)

if __name__ == "__main__":
    app = FlashcardApp()
    app.run()
