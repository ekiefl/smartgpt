import cattrs

import smartgpt.user_profile
from smartgpt.chat import Agent, SmartGPT
from smartgpt.datatypes import (
    Credentials,
    GPTConfig,
    Message,
    Mode,
    Response,
    Role,
    Settings,
)
from smartgpt.strenum import StrEnum

cattrs.register_unstructure_hook(
    StrEnum,
    lambda v: v.value,
)
