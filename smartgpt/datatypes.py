"""
This module defines fundamental data types and configurations for interacting with
the GPT model. It provides enums for interaction modes and roles, structures for
messages, responses and configurations.

Classes:
    Mode:
        Enum representing the different modes of interaction.
    GPTConfig:
        Configuration for the GPT model.
    Role:
        Enum representing the different roles in a conversation.
    Message:
        Structure for encapsulating a message in a conversation.
    Response:
        Structure for encapsulating a response from the GPT model.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import attrs
import cattrs
import yaml

from smartgpt import strenum
from smartgpt.util import Pathish


@attrs.define
class Settings:
    generator_temps: List[float]
    researcher_temp: float
    resolver_temp: float
    model: str
    mode: Mode
    credentials: Credentials
    debug: bool

    @property
    def num_agents(self) -> int:
        return len(self.generator_temps)

    def save(self, path: Pathish) -> Path:
        path = Path(path)
        with path.open("w") as file:
            yaml.dump(cattrs.unstructure(self), file)

        return path

    @classmethod
    def load(cls, path: Pathish) -> Settings:
        path = Path(path)
        if not path.is_file():
            raise Exception(f"{path} is not a file")

        with path.open("r") as file:
            data = yaml.safe_load(file)

        return cattrs.structure(data, cls)

    @classmethod
    def default(cls) -> Settings:
        return cls(
            generator_temps=[0.5, 0.5, 0.5],
            researcher_temp=0.5,
            resolver_temp=0.5,
            model="gpt-4",
            mode=Mode.RESOLVER,
            credentials=Credentials.dummy(),
            debug=False,
        )


@attrs.define
class Credentials:
    key: str

    @classmethod
    def dummy(cls) -> Credentials:
        return cls("XXXXXX")


class Mode(strenum.StrEnum):
    """Enum representing the different modes of interaction."""

    ZERO_SHOT = strenum.auto()
    STEP_BY_STEP = strenum.auto()
    RESOLVER = strenum.auto()


@attrs.define(frozen=True)
class GPTConfig:
    """Configuration for the GPT model.

    Attributes:
        model:
            The GPT model to use (default is 'gpt-4').
        credentials:
            Credentials for accessing the model.
        mode:
            The mode of interaction.
    """

    model: str = attrs.field(default="gpt-4")
    credentials: Credentials = attrs.field(default=Settings.default().credentials)
    mode: Mode = attrs.field(default=Mode.ZERO_SHOT)

    @classmethod
    def default(cls) -> GPTConfig:
        """Factory method to create a default GPTConfig.

        Returns:
            GPTConfig:
                A GPTConfig instance with default values.
        """
        return cls()


class Role(strenum.StrEnum):
    """Enum representing the different roles in a conversation"""

    USER = strenum.auto()
    ASSISTANT = strenum.auto()
    SYSTEM = strenum.auto()


@attrs.define(frozen=True)
class Message:
    """Structure for encapsulating a message in a conversation.

    Attributes:
        role:
            The role of the sender of the message.
        content:
            The content of the message.
    """

    role: Role
    content: str


@attrs.define
class Response:
    """Structure for encapsulating a response from the GPT model.

    Attributes:
        message:
            The message from the model.
        total_tokens:
            The total number of tokens used.
        finish_reason:
            The reason for finishing the response.
    """

    message: Message
    total_tokens: int
    finish_reason: str

    @classmethod
    def from_openai_response(cls, response) -> Response:
        """Factory method to create a Response from an OpenAI API response.

        Args:
            response:
                The response from the OpenAI API.

        Returns:
            Response:
                A Response instance with values from the API response.
        """
        return cls(
            message=cattrs.structure(response["choices"][0]["message"], Message),
            total_tokens=response["usage"]["total_tokens"],
            finish_reason=response["choices"][0]["finish_reason"],
        )
