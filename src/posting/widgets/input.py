import os
import shlex
import subprocess
import tempfile

from rich.style import Style
from textual.binding import Binding
from textual.theme import Theme
from textual.widgets import Input

from posting.config import SETTINGS


class PostingInput(Input):
    BINDINGS = [
        Binding("ctrl+e", "open_in_editor", "Editor", id="open-in-editor"),
    ]

    def on_mount(self) -> None:
        self.cursor_blink = SETTINGS.get().text_input.blinking_cursor

        self._theme_cursor_style: Style | None = None

        self.on_theme_change(self.app.current_theme)
        self.app.theme_changed_signal.subscribe(self, self.on_theme_change)

    @property
    def cursor_style(self) -> Style:
        return (
            self._theme_cursor_style
            if self._theme_cursor_style is not None
            else self.get_component_rich_style("input--cursor")
        )

    def on_theme_change(self, theme: Theme) -> None:
        cursor_style = theme.variables.get("input-cursor")
        self._theme_cursor_style = Style.parse(cursor_style) if cursor_style else None
        self.refresh()

    def action_open_in_editor(self) -> None:
        editor_command = SETTINGS.get().editor
        if not editor_command:
            self.app.notify(
                severity="warning",
                title="No editor configured",
                message="Set the [b]$EDITOR[/b] environment variable.",
            )
            return

        editor_args = shlex.split(editor_command)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_name = temp_file.name
            temp_file.write(self.value.encode("utf-8"))
            temp_file.flush()

        editor_args.append(temp_file_name)

        with self.app.suspend():
            try:
                subprocess.call(editor_args)
            except OSError:
                self.app.notify(
                    severity="error",
                    title="Can't run command",
                    message=f"The command [b]{editor_command}[/b] failed to run.",
                )

        with open(temp_file_name, "r", encoding="utf-8") as temp_file:
            self.value = temp_file.read().strip()

        os.remove(temp_file_name)
        self.app.refresh()
