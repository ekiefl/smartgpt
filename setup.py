#! /usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="smartgpt",
    version="0.1.0",
    packages=find_packages(),
    scripts=["bin/smartgpt"],
    author_email="kiefl.evan@gmail.com",
    author="Evan Kiefl",
    url="https://github.com/ekiefl/smartgpt",
    install_requires=[
        "openai",
        "attrs",
        "cattrs",
        "pyyaml",
        "prompt_toolkit",
    ],
    include_package_data=True,
    zip_safe=False,
)
