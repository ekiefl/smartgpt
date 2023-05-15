#! /usr/bin/env python

import sys
import textwrap

tty_colors = {
    "gray": {"normal": "\033[1;30m%s\033[1m", "bold": "\033[0;30m%s\033[0m"},
    "red": {"normal": "\033[1;31m%s\033[1m", "bold": "\033[0;31m%s\033[0m"},
    "green": {"normal": "\033[1;32m%s\033[1m", "bold": "\033[0;32m%s\033[0m"},
    "yellow": {"normal": "\033[1;33m%s\033[1m", "bold": "\033[0;33m%s\033[0m"},
    "blue": {"normal": "\033[1;34m%s\033[1m", "bold": "\033[0;34m%s\033[0m"},
    "magenta": {"normal": "\033[1;35m%s\033[1m", "bold": "\033[0;35m%s\033[0m"},
    "cyan": {"normal": "\033[1;36m%s\033[1m", "bold": "\033[0;36m%s\033[0m"},
    "white": {"normal": "\033[1;37m%s\033[1m", "bold": "\033[0;37m%s\033[0m"},
    "crimson": {"normal": "\033[1;38m%s\033[1m", "bold": "\033[0;38m%s\033[0m"},
}


def color_text(text, color="crimson", weight="bold"):
    if sys.stdout.isatty():
        return tty_colors[color][weight] % text
    else:
        return text


def remove_spaces(text):
    if not text:
        return ""

    while True:
        if text.find("  ") > -1:
            text = text.replace("  ", " ")
        else:
            break

    return text


class SmartGPTError(Exception):
    def __init__(self, e=None):
        self.e = remove_spaces(e)
        self.error_type = "SmartGPT Error"
        Exception.__init__(self)
        return

    def __str__(self):
        max_len = max([len(line) for line in textwrap.fill(self.e, 80).split("\n")])
        error_lines = [
            "%s%s" % (line, " " * (max_len - len(line)))
            for line in textwrap.fill(self.e, 80).split("\n")
        ]

        error_message = [
            "%s: %s" % (color_text(self.error_type, "red"), error_lines[0])
        ]
        for error_line in error_lines[1:]:
            error_message.append(
                "%s%s" % (" " * (len(self.error_type) + 2), error_line)
            )

        return "\n\n" + "\n".join(error_message) + "\n\n"

    def clear_text(self):
        return self.e
