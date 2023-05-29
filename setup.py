#! /usr/bin/env python

import sys

from setuptools import find_packages, setup


def error_msg() -> str:
    msg = "ERROR: SmartGPT doesn't support python <3.8"
    return "v" * len(msg) + f"\n{msg}\n" + "^" * len(msg)


if sys.version_info < (3, 8):
    sys.exit(error_msg())

setup(
    name="smartgpt",
    version="0.1.3",
    packages=find_packages(),
    scripts=["bin/smartgpt"],
    author_email="kiefl.evan@gmail.com",
    author="Evan Kiefl",
    url="https://github.com/ekiefl/smartgpt",
    install_requires=[
        "openai",
        "attrs",
        "cattrs",
        "pandas",
        "pyyaml",
        "prompt_toolkit",
    ],
    include_package_data=True,
    zip_safe=False,
)
