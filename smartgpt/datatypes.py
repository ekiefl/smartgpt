from __future__ import annotations

from smartgpt import strenum


class Verbosity(strenum.StrEnum):
    NONE = strenum.auto()
    SOME = strenum.auto()
    ALL = strenum.auto()


class Mode(strenum.StrEnum):
    """Enum representing the different modes of interaction."""

    ZERO_SHOT = strenum.auto()
    STEP_BY_STEP = strenum.auto()
    RESOLVER = strenum.auto()
