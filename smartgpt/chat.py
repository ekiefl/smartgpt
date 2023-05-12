from __future__ import annotations

from typing import Dict, List, Tuple

import attrs
import openai
from openai.error import InvalidRequestError

from smartgpt import prompts
from smartgpt.credentials import Credentials
from smartgpt.datatypes import GPTConfig, Message, Mode, Response, Role
from smartgpt.util import REPLColors

USER_PREFIX = REPLColors.OKGREEN + "> " + REPLColors.ENDC
GPT_PREFIX = REPLColors.OKBLUE + "\n" + REPLColors.ENDC


@attrs.define
class Agent:
    messages: List[Dict[str, str]] = attrs.field(factory=list)
    credentials: Credentials = attrs.field(factory=Credentials.default)
    model: str = attrs.field(default="gpt-4")
    temp: float = attrs.field(default=0.5)
    token_counts: Dict[int, int] = attrs.field(factory=dict)

    def append_message(self, message: Message) -> None:
        self.messages.append(attrs.asdict(message))

    def request(self) -> Response:
        return Response.from_openai_response(
            openai.ChatCompletion.create(
                model=self.model,
                messages=self.messages,
                api_key=self.credentials.key,
            )
        )

    def response(self, prompt: str) -> Message:
        self.append_message(Message(Role.USER, prompt))

        try:
            response = self.request()
        except InvalidRequestError:
            raise NotImplementedError()

        self.append_message(response.message)
        self.token_counts[len(self.messages)] = response.total_tokens

        return response.message


@attrs.define
class SmartGPT:
    config: GPTConfig
    main: Agent
    researcher: Agent
    resolver: Agent
    generators: List[Agent]

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

        response = self.create_response(prompt)

        if not quiet:
            print(GPT_PREFIX + response.content + "\n")

        return prompt, response.content

    def create_response(self, prompt: str) -> Message:
        if self.config.mode == Mode.ZERO_SHOT:
            response = self.main.response(prompt)

        elif self.config.mode == Mode.STEP_BY_STEP:
            response = self.main.response(prompts.step_by_step(prompt))

        elif self.config.mode == Mode.RESOLVER:
            candidates: List[str] = []
            for generator in self.generators:
                generator.messages = self.main.messages
                generator.token_counts = self.main.token_counts
                candidates.append(generator.response(prompt).content)

            self.researcher.messages = self.main.messages
            self.researcher.token_counts = self.main.token_counts
            self.researcher.response(prompts.you_are_a_researcher(prompt, candidates))

            self.resolver.messages = self.researcher.messages
            self.resolver.token_counts = self.researcher.token_counts
            response = self.resolver.response(prompts.you_are_a_resolver())

        return response


if __name__ == "__main__":
    app = SmartGPT()
    app.repl()
