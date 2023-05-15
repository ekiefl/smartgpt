from typing import Protocol, Tuple

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.history import FileHistory

from smartgpt.datatypes import Message
from smartgpt.settings.constants import REPL_HISTORY_PATH
from smartgpt.settings.user import UserSettings

MAX_HISTORY = 3000


class LimitedFileHistory(FileHistory):
    def __init__(self, filename, max_size):
        super().__init__(filename)
        self.max_size = max_size

    def append_string(self, string):
        super().append_string(string)
        self.limit_file_size()

    def limit_file_size(self):
        with open(self.filename, "r+") as f:
            lines = f.readlines()
            if len(lines) > self.max_size:
                f.seek(0)
                f.truncate()
                f.writelines(lines[-self.max_size :])  # Keep last max_size lines


session: PromptSession = PromptSession(
    history=LimitedFileHistory(str(REPL_HISTORY_PATH), MAX_HISTORY),
    multiline=True,
    wrap_lines=True,
    vi_mode=UserSettings.default().vi_mode,
)


USER_PREFIX = FormattedText(
    [
        ("", "(To submit: press ESC, then ENTER)\n"),
        ("bold fg:ansigreen", "> "),
    ]
)


class Model(Protocol):
    def create_response(self, prompt: str) -> Message:
        ...


def repl(model: Model) -> None:
    """Starts the Read-Eval-Print-Loop (REPL) for interaction with a model

    This function runs indefinitely until the session is manually terminated.
    """
    while True:
        _, _ = repl_iteration(model)


def repl_iteration(model: Model, quiet=False) -> Tuple[str, str]:
    """Executes a single pass of the Read-Eval-Print-Loop (REPL)

    Args:
        quiet:
            If true, the function will not print the model's response. Default is
            False.

    Returns:
        Tuple[str, str]:
            The user's prompt and the model's response.
    """
    prompt = session.prompt(USER_PREFIX)

    response_message = model.create_response(prompt)

    if not quiet:
        print(f"\n{response_message.content}\n")

    return prompt, response_message.content
