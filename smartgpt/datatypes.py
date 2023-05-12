from __future__ import annotations

import attrs
import cattrs

from smartgpt import strenum
from smartgpt.credentials import Credentials


class Mode(strenum.StrEnum):
    ZERO_SHOT = strenum.auto()
    STEP_BY_STEP = strenum.auto()
    RESOLVER = strenum.auto()


@attrs.define(frozen=True)
class GPTConfig:
    model: str = attrs.field(default="gpt-4")
    credentials: Credentials = attrs.field(factory=Credentials.default)
    mode: Mode = attrs.field(default=Mode.ZERO_SHOT)

    @classmethod
    def default(cls) -> GPTConfig:
        return cls()


class Role(strenum.StrEnum):
    USER = strenum.auto()
    ASSISTANT = strenum.auto()
    SYSTEM = strenum.auto()


@attrs.define(frozen=True)
class Message:
    role: Role
    content: str


@attrs.define
class Response:
    message: Message
    total_tokens: int
    finish_reason: str

    @classmethod
    def from_openai_response(cls, response) -> Response:
        return cls(
            message=cattrs.structure(response["choices"][0]["message"], Message),
            total_tokens=response["usage"]["total_tokens"],
            finish_reason=response["choices"][0]["finish_reason"],
        )
