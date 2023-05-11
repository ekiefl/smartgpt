from __future__ import annotations

from typing import Dict, List, Tuple

import attrs
import openai
from openai.error import InvalidRequestError

from smartgpt.datatypes import ChatConfig, Message, Response, Role
from smartgpt.util import REPLColors

USER_PREFIX = REPLColors.OKGREEN + "> " + REPLColors.ENDC
GPT_PREFIX = REPLColors.OKBLUE + "\n" + REPLColors.ENDC


def get_response(messages: List[Dict[str, str]], config: ChatConfig) -> Response:
    return Response.from_openai_response(
        openai.ChatCompletion.create(
            model=config.model,
            messages=messages,
            api_key=config.credentials.key,
        )
    )


@attrs.define
class SmartGPT:
    messages: List[Dict[str, str]] = attrs.field(factory=list)
    config: ChatConfig = attrs.field(factory=ChatConfig.default)
    token_counts: Dict[int, int] = attrs.field(factory=dict)

    def bot_response(self, response: str) -> None:
        print(GPT_PREFIX + response + "\n")

    def repl(self) -> None:
        """Starts the REPL"""
        while True:
            _, _ = self.repl_iteration()

    def repl_iteration(self, quiet=False) -> Tuple[str, str]:
        """A single Read-Eval-Print-Loop pass

        Returns:
            prompt, reponse:
                What the user typed and what the response was.
        """
        prompt = input(USER_PREFIX)

        response = self.chat(prompt)

        if not quiet:
            self.bot_response(response)

        return prompt, response

    def append_message(self, message: Message) -> None:
        self.messages.append(attrs.asdict(message))

    def chat(self, message_string: str) -> str:
        self.append_message(Message(Role.USER, message_string))

        try:
            response = get_response(self.messages, self.config)
        except InvalidRequestError:
            raise NotImplementedError()

        self.append_message(response.message)
        self.token_counts[len(self.messages)] = response.total_tokens

        return response.message.content


if __name__ == "__main__":
    app = SmartGPT()
    app.repl()
