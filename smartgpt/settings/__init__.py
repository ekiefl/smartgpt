import cattrs

from smartgpt import strenum
from smartgpt.settings.credentials import Credentials
from smartgpt.settings.user import UserSettings

cattrs.register_unstructure_hook(
    strenum.StrEnum,
    lambda v: v.value,
)

UserSettings.check()
Credentials.check()
