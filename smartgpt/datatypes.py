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

import attrs
import cattrs

from smartgpt import strenum
from smartgpt.credentials import Credentials


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
    credentials: Credentials = attrs.field(factory=Credentials.default)
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
