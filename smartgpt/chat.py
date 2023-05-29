from __future__ import annotations

import copy
import logging
from typing import List, Optional

import attrs

from smartgpt import prompts
from smartgpt.datatypes import Mode, Verbosity
from smartgpt.logger import get_logger
from smartgpt.message import GPTBot, Message, Role
from smartgpt.repl import repl
from smartgpt.settings.credentials import Credentials
from smartgpt.settings.user import UserSettings


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
    credentials: Credentials = attrs.field(default=Credentials.default())
    mode: Mode = attrs.field(default=Mode.ZERO_SHOT)

    @classmethod
    def default(cls) -> GPTConfig:
        """Factory method to create a default GPTConfig.

        Returns:
            GPTConfig:
                A GPTConfig instance with default values.
        """
        return cls()


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
    main: GPTBot
    researcher: GPTBot
    resolver: GPTBot
    generators: List[GPTBot]
    verbosity: Verbosity = Verbosity.SOME

    logger: logging.Logger = attrs.field(init=False)

    def __attrs_post_init__(self) -> None:
        self.logger = get_logger(verbosity=self.verbosity)

    def response(self, prompt: str) -> Message:
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

        self.logger.debug(f"Creating response for prompt: '{prompt}'")

        if self.config.mode == Mode.ZERO_SHOT:
            self.logger.info("Generating response for zero-shot prompt...")
            self.logger.debug("Mode: ZERO_SHOT")

            response = self.main.response(prompt)
            self.logger.debug(f"ZERO_SHOT response:\n{response.content}")

        elif self.config.mode == Mode.STEP_BY_STEP:
            self.logger.info(
                "Generating response for chain-of-thought-flavored prompt..."
            )
            self.logger.debug("Mode: STEP_BY_STEP")

            transformed_prompt = prompts.step_by_step(prompt)
            self.logger.debug(f"Transformed prompt:\n{transformed_prompt}")

            response = self.main.response(transformed_prompt)
            self.logger.debug(f"STEP_BY_STEP response:\n{response.content}")

        elif self.config.mode == Mode.RESOLVER:
            self.logger.debug("Mode: RESOLVER")

            candidates: List[str] = []
            candidate_prompt = prompts.step_by_step(prompt)
            self.logger.debug(f"Prompt for generators:\n{candidate_prompt}")

            for i, generator in enumerate(self.generators):
                self.logger.info(f"Generating response for generator {i+1}...")

                generator.messages = copy.deepcopy(self.main.messages)

                candidate = generator.response(candidate_prompt).content
                candidates.append(candidate)
                self.logger.debug(f"Generator {i+1} response:\n{candidate}")

            self.logger.info("Generating response for researcher...")

            researcher_prompt = prompts.you_are_a_researcher(prompt, candidates)
            self.logger.debug(f"Researcher prompt:\n{researcher_prompt}")

            self.researcher.messages = copy.deepcopy(self.main.messages)

            researcher_response = self.researcher.response(researcher_prompt)
            self.logger.debug(f"Researcher response:\n{researcher_response.content}")

            self.logger.info("Generating response for resolver...")

            resolver_prompt = prompts.you_are_a_resolver(
                candidates, silence_rationale=True
            )
            self.logger.debug(f"Resolver prompt:\n{resolver_prompt}")

            self.resolver.messages = copy.deepcopy(self.researcher.messages)
            response = self.resolver.response(resolver_prompt)
            self.logger.debug(f"Resolver response:\n{response.content}")

            # Add the prompt and response to the main agent
            self.main.append_message(Message(Role.USER, candidate_prompt))
            self.main.append_message(response)

        logging.debug("Finished generating response")

        return response

    @classmethod
    def create(
        cls,
        settings: Optional[UserSettings] = None,
        credentials: Optional[Credentials] = None,
        mode: Optional[Mode] = None,
    ) -> SmartGPT:
        if settings is None:
            settings = UserSettings.default()

        if credentials is None:
            credentials = Credentials.default()

        if mode is not None:
            settings.mode = mode

        return cls(
            config=GPTConfig(
                credentials=credentials,
                model=settings.model,
                mode=settings.mode,
            ),
            main=GPTBot(
                credentials=credentials,
                model=settings.model,
                temp=settings.resolver_temp,
            ),
            researcher=GPTBot(
                credentials=credentials,
                model=settings.model,
                temp=settings.researcher_temp,
            ),
            resolver=GPTBot(
                credentials=credentials,
                model=settings.model,
                temp=settings.resolver_temp,
            ),
            generators=[
                GPTBot(
                    credentials=credentials,
                    model=settings.model,
                    temp=settings.generator_temps[i],
                )
                for i in range(settings.num_agents)
            ],
            verbosity=settings.verbosity,
        )

    def repl(self) -> None:
        repl(self)
