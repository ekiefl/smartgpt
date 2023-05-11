from pathlib import Path
from typing import Union

Pathish = Union[str, Path]


class REPLColors:
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    ENDC = "\033[0m"
