from pathlib import Path

from smartgpt.datatypes import Credentials, Settings

SETTINGS_DIR = Path.home() / ".smartgpt"
SETTINGS_DIR.mkdir(exist_ok=True)

SETTINGS_PATH = SETTINGS_DIR / "settings.yaml"
if not SETTINGS_PATH.exists():
    Settings.default().save(SETTINGS_PATH)

settings = Settings.load(SETTINGS_PATH)
if settings.credentials == (dummy := Credentials.dummy()):
    raise ValueError(
        f"In order to use Smart-GPT, you need an API key. Get yours at "
        f"https://platform.openai.com/account/api-keys, then open '{SETTINGS_PATH}' "
        f"and replace '{dummy.key}' with your API key."
    )
