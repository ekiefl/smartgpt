from __future__ import annotations

from pathlib import Path
from typing import List

import attrs
import cattrs
import yaml

from smartgpt.datatypes import Mode, Verbosity
from smartgpt.settings.constants import SETTINGS_PATH, USER_DIR
from smartgpt.settings.credentials import Credentials
from smartgpt.util import Pathish


@attrs.define
class UserSettings:
    generator_temps: List[float]
    researcher_temp: float
    resolver_temp: float
    model: str
    mode: Mode
    credentials: Credentials
    verbosity: Verbosity
    vi_mode: bool

    def __repr__(self):
        margin = " " * 4
        lines = [f"\n{margin}Settings"]
        middle_prefix = f"{margin}├── "
        final_prefix = f"{margin}└── "

        attr_names = [attr.name for attr in attrs.fields(UserSettings)]
        max_len = max(len(attr_name) for attr_name in attr_names)

        for idx, attr_name in enumerate(attr_names):
            attr_val = getattr(self, attr_name)
            spacer = " " * (max_len - len(attr_name))
            prefix = final_prefix if idx == len(attr_names) - 1 else middle_prefix
            lines.append(f"{prefix}{attr_name}{spacer} = {attr_val.__str__()}")

        return "\n".join(lines) + "\n"

    @property
    def num_agents(self) -> int:
        return len(self.generator_temps)

    def save(self, path: Pathish) -> Path:
        path = Path(path)
        with path.open("w") as file:
            yaml.dump(cattrs.unstructure(self), file)

        return path

    @classmethod
    def load(cls, path: Pathish) -> UserSettings:
        path = Path(path)
        if not path.is_file():
            raise Exception(f"{path} is not a file")

        with path.open("r") as file:
            data = yaml.safe_load(file)

        return cattrs.structure(data, cls)

    @classmethod
    def default(cls) -> UserSettings:
        cls.check()
        return cls.load(SETTINGS_PATH)

    @classmethod
    def fallback(cls) -> UserSettings:
        return cls(
            generator_temps=[0.7, 0.7, 0.7],
            researcher_temp=0.5,
            resolver_temp=0.5,
            model="gpt-4",
            mode=Mode.RESOLVER,
            credentials=Credentials.dummy(),
            verbosity=Verbosity.SOME,
            vi_mode=False,
        )

    @classmethod
    def check(cls) -> Path:
        """Create settings directory and fallback settings file if doesn't exist"""
        USER_DIR.mkdir(exist_ok=True)

        if not SETTINGS_PATH.exists():
            cls.fallback().save(SETTINGS_PATH)

        return SETTINGS_PATH
