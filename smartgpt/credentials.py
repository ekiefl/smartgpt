from __future__ import annotations

from pathlib import Path

import attrs

from smartgpt.util import Pathish

DEFAULT_PATH = Path(__file__).parent.parent / ".credentials"


@attrs.define
class Credentials:
    key: str

    @classmethod
    def from_file(cls, path: Pathish) -> Credentials:
        return cls(open(path).read().strip())

    @classmethod
    def default(cls) -> Credentials:
        try:
            return cls.from_file(DEFAULT_PATH)
        except FileNotFoundError:
            expected_dir = DEFAULT_PATH.parent
            raise FileNotFoundError(
                f"Woops, I was expecting a GPT credentials file '.credentials' in "
                f"the directory '{expected_dir}', but it's missing. Create that file, "
                f"placing your GPT as the first and only line."
            )
