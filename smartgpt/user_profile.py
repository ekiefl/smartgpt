import sys
from pathlib import Path

from smartgpt.datatypes import Credentials, Settings
from smartgpt.error import SmartGPTError

SETTINGS_DIR = Path.home() / ".smartgpt"
SETTINGS_DIR.mkdir(exist_ok=True)

SETTINGS_PATH = SETTINGS_DIR / "settings.yaml"
if not SETTINGS_PATH.exists():
    Settings.fallback().save(SETTINGS_PATH)


def get_settings() -> Settings:
    return Settings.load(SETTINGS_PATH)


settings = get_settings()
if settings.credentials == (dummy := Credentials.dummy()):
    print(
        SmartGPTError(
            f"Almost! In order to use Smart-GPT, you need your OpenAI API key. Get "
            f"yours at https://platform.openai.com/account/api-keys, then open "
            f"'{SETTINGS_PATH}' and replace '{dummy.key}' with your API key."
        )
    )
    sys.exit(1)

REPL_HISTORY_PATH = SETTINGS_DIR / "history.txt"
MAX_HISTORY = 3000
