from __future__ import annotations

import sys
from pathlib import Path

import attrs

from smartgpt.error import SmartGPTError
from smartgpt.settings.constants import CREDENTIALS_PATH, USER_DIR
from smartgpt.util import Pathish

DUMMY_KEY = "XXXXXX"


def _api_key_repr(key: str) -> str:
    if key == DUMMY_KEY:
        return key

    assert len(key) > 8
    return key[:4] + "*" * 4 + key[-4:]


@attrs.define
class Credentials:
    key: str = attrs.field(repr=_api_key_repr)

    def save(self, path: Pathish) -> Path:
        path = Path(path)
        with path.open("w") as fp:
            fp.write(self.key)

        return path

    @classmethod
    def load(cls, path: Pathish) -> Credentials:
        path = Path(path)
        assert path.is_file()

        with path.open("r") as fp:
            return cls(fp.read().strip())

    @classmethod
    def default(cls) -> Credentials:
        cls.check()
        return cls.load(CREDENTIALS_PATH)

    @classmethod
    def dummy(cls) -> Credentials:
        return cls(DUMMY_KEY)

    @classmethod
    def check(cls) -> None:
        if not CREDENTIALS_PATH.exists():
            USER_DIR.mkdir(exist_ok=True)
            cls.dummy().save(CREDENTIALS_PATH)

        if cls.load(CREDENTIALS_PATH).key == DUMMY_KEY:
            error = SmartGPTError(
                f"Almost! In order to use Smart-GPT, you need your OpenAI API key. Get "
                f"yours at https://platform.openai.com/account/api-keys, then open "
                f"'{CREDENTIALS_PATH}' and replace '{DUMMY_KEY}' with your API key."
            )
            print(error)
            sys.exit()
