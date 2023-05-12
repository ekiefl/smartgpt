"""This module is a wrapper around OpenAI's GPT model

It defines two main classes, Agent
and SmartGPT, which together facilitate interactive sessions with the AI model. The
module supports different modes of interaction, including zero-shot, "step-by-step"
chain of thought prompt flavoring, and the full "SmartGPT" resolver mode.

Classes:
    Agent:
        Represents an interface to the GPT model.
    SmartGPT:
        Manages interactive sessions with the AI, supporting different modes of
        interaction.
"""

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
    """Represents an interface to the GPT model.

    It encapsulates the process of sending
    messages to the model and receiving responses. The class also handles token count
    management and message history.

    Attributes:
        messages:
            A list of messages sent to and received from the model.
        credentials:
            Credentials for accessing the model.
        model:
            The model to use (default is 'gpt-4').
        temp:
            The temperature parameter to use when generating responses.
        token_counts:
            A dictionary mapping the length of the message history to the total token
            count.
    """

    messages: List[Dict[str, str]] = attrs.field(factory=list)
    credentials: Credentials = attrs.field(factory=Credentials.default)
    model: str = attrs.field(default="gpt-4")
    temp: float = attrs.field(default=0.5)
    token_counts: Dict[int, int] = attrs.field(factory=dict)

    def append_message(self, message: Message) -> None:
        """Appends a message to the current message history.

        Args:
            message: The message to append.
        """
        self.messages.append(attrs.asdict(message))

    def request(self) -> Response:
        """Sends the current message history to the GPT model via an API request

        The message history includes all previous interactions, which allows the model
        to generate a response based on the entire conversation context.

        Returns:
            Response:
                A Response object that encapsulates the model's response, which includes
                the generated message, remaining tokens, and other metadata.
        """
        return Response.from_openai_response(
            openai.ChatCompletion.create(
                model=self.model,
                messages=self.messages,
                api_key=self.credentials.key,
            )
        )

    def response(self, prompt: str) -> Message:
        """Appends prompt to message history and sends request to the GPT model.

        The model's response is then appended to the message history, and the total
        tokens used is updated.

        Args:
            prompt:
                The prompt to send to the model.

        Returns:
            Message:
                The model's response encapsulated in a Message object.
        """
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
    """Manages interactive sessions with the AI, supports different interaction modes.

    In zero-shot mode, the user's prompts are sent directly to the model. In
    step-by-step mode, prompts are flavored with the "step-by-step" chain of thought
    prompt. In resolver mode, the "SmartGPT" mode is used, where multiple agents
    generate responses, which are scrutinized by a researcher agent and then a final
    response is chosen by a resolver agent.

    Attributes:
        config:
            The configuration for the interaction.
        main:
            The main agent, responsible for sending prompts, receiving responses, and
            most importantly, storing a linear chat history.
        researcher:
            An agent responsible for scrutinizing generator responses.
        resolver:
            An agent responsible for considering the researcher's analysis and creating
            the final response.
        generators:
            A list of agents for generating responses in resolver mode.
    """

    config: GPTConfig
    main: Agent
    researcher: Agent
    resolver: Agent
    generators: List[Agent]

    def repl(self) -> None:
        """Starts the Read-Eval-Print-Loop (REPL) for interaction with the model

        This function runs indefinitely until the session is manually terminated.
        """
        while True:
            _, _ = self.repl_iteration()

    def repl_iteration(self, quiet=False) -> Tuple[str, str]:
        """Executes a single pass of the Read-Eval-Print-Loop (REPL)

        Args:
            quiet:
                If true, the function will not print the model's response. Default is
                False.

        Returns:
            Tuple[str, str]:
                The user's prompt and the model's response.
        """
        prompt = input(USER_PREFIX)

        response = self.create_response(prompt)

        if not quiet:
            print(GPT_PREFIX + response.content + "\n")

        return prompt, response.content

    def create_response(self, prompt: str) -> Message:
        """
        Determines the mode of interaction based on the current configuration and
        generates a response from the model accordingly.

        In ZERO_SHOT mode, the prompt is sent directly to the main agent, which sends it
        to the model and returns the response.

        In STEP_BY_STEP mode, the prompt is transformed using the `prompts.step_by_step`
        function before being sent to the model. The transformed prompt is intended to
        guide the model to generate a more detailed response.

        In RESOLVER mode, multiple generators create potential responses to the prompt.
        The researcher agent points out the flaws in each generated response. Finally,
        the resolver agent combines the selected responses into a final response.

        Args:
            prompt:
                The prompt to send to the model.

        Returns:
            Message:
                The model's response encapsulated in a Message object.
        """
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
