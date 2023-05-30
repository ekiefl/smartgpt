from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import List, Optional, Tuple

import attrs
import pandas as pd

from smartgpt import GPTBot, Mode, SmartGPT, UserSettings, Verbosity
from smartgpt.data import get_prompt, tests


def override_settings_with_CLI_args(
    settings: UserSettings, args: argparse.Namespace
) -> UserSettings:
    """Overwrites settings attributes with those specified in CLI"""
    if args.verbosity:
        settings.verbosity = args.verbosity
    if args.model:
        settings.model = args.model

    return settings


def get_questions(N: int, subjects: Optional[List[str]] = None) -> pd.DataFrame:
    if subjects is None:
        subjects = list(tests.keys())

    for subject in subjects:
        assert subject in tests
        assert tests[subject].shape[0] >= N, f"'{subject}' < {N} questions"

    return pd.concat(
        (
            tests[subject]
            .iloc[:N]
            .reset_index()
            .rename(columns={"index": "question_idx"})
            for subject in subjects
        ),
        ignore_index=True,
    )


def create_competitors(settings: UserSettings) -> Tuple[SmartGPT, SmartGPT, SmartGPT]:
    """Returns bots for gpt, chain-of-though gpt, and smartgpt"""
    return (
        SmartGPT.create(settings=settings, mode=Mode.ZERO_SHOT),
        SmartGPT.create(settings=settings, mode=Mode.STEP_BY_STEP),
        SmartGPT.create(settings=settings, mode=Mode.RESOLVER),
    )


def get_responses(prompt: str, settings: UserSettings) -> Tuple[str, ...]:
    """Returns fresh bot responses for gpt, chain-of-though gpt, and smartgpt"""
    while True:
        try:
            return tuple(
                bot.response(prompt).content for bot in create_competitors(settings)
            )
        except:
            print("Uncaught error raised. Sleeping for 20 and trying again.")
            time.sleep(20)


def create_grader() -> GPTBot:
    return GPTBot(
        messages=[
            {
                "role": "system",
                "content": (
                    "You grade multiple choice questions. You will always be given "
                    "the correct answer (A, B, C, or D) as well as the student's "
                    "answer, which may contain logic and justification for. Your job "
                    "is to scan their answer and determine whether or not the student "
                    "got the right answer unambiguously. You should produce "
                    "machine-like output, and are only capable of two responses: "
                    "'correct' or 'incorrect'."
                ),
            }
        ]
    )


def get_grader_prompt(response: str, answer: str) -> str:
    return f"The correct answer is {answer}.\n\nThe student wrote:\n\n{response}"


def is_correct(response: str, answer: str) -> bool:
    grader = create_grader()

    while True:
        try:
            grade = grader.response(get_grader_prompt(response, answer)).content
            break
        except:
            print("Uncaught error raised. Sleeping for 20 and trying again.")
            time.sleep(20)

    if grade == "correct":
        return True
    elif grade == "incorrect":
        return False
    else:
        # The grader has failed to do its job. Conservatively mark incorrect
        print(f"WARNING: grader failed to produce 'correct' or 'incorrect': {grade}")
        return False


def get_initial_scoresheet(path: str) -> pd.DataFrame:
    if Path(path).exists():
        return pd.read_csv(path, sep="\t")

    return pd.DataFrame({}, columns=list(attrs.fields_dict(Entry).keys()))


def save_entry_to_scoresheet(
    scoresheet: pd.DataFrame, entry: Entry, output: str
) -> pd.DataFrame:
    scoresheet = pd.concat(
        [scoresheet, pd.DataFrame(attrs.asdict(entry), index=[0])], ignore_index=True
    )
    scoresheet.to_csv(Path(output), sep="\t", index=False)
    return scoresheet


@attrs.define
class Entry:
    subject: str
    question_idx: int
    question: str
    A: str
    B: str
    C: str
    D: str
    answer: str
    prompt: str
    gpt4_correct: bool
    gpt4_response: str
    gpt4cot_correct: bool
    gpt4cot_response: str
    smartgpt_correct: bool
    smartgpt_response: str
    manually_verified: bool


def main(args):
    settings = override_settings_with_CLI_args(UserSettings.default(), args)
    scoresheet = get_initial_scoresheet(args.output)

    if args.subject:
        questions_frame = get_questions(args.N, [args.subject])
    else:
        questions_frame = get_questions(args.N)

    for _, question in questions_frame.iterrows():
        prompt = get_prompt(question)
        gpt, cot, smart = get_responses(prompt, settings)

        entry = Entry(
            subject=question["subject"],
            question_idx=question["question_idx"],
            question=question["question"],
            A=question["A"],
            B=question["B"],
            C=question["C"],
            D=question["D"],
            answer=question["answer"],
            prompt=prompt,
            gpt4_response=gpt,
            gpt4cot_response=cot,
            smartgpt_response=smart,
            gpt4_correct=is_correct(gpt, question["answer"]),
            gpt4cot_correct=is_correct(cot, question["answer"]),
            smartgpt_correct=is_correct(smart, question["answer"]),
            manually_verified=False,
        )

        scoresheet = save_entry_to_scoresheet(scoresheet, entry, args.output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Output TSV of scoresheet")
    parser.add_argument(
        "-N", required=True, type=int, help="The number of questions per subject"
    )
    parser.add_argument(
        "--subject",
        required=False,
        default=None,
        help=(
            "If not provided, all subjects are used. For available subjects see "
            "`from smartgpt.data import tests; tests.keys()`"
        ),
    )
    parser.add_argument(
        "--verbosity",
        required=False,
        choices=[verbosity.value for verbosity in Verbosity],
        help=(
            "Sets the amount that shows up on your screen.\n"
            "\n"
            "1. `none`: Only the final response shows.\n"
            "\n"
            "2. `some`: Status updates are provided so you know where in the response "
            "creation SmartGPT is at.\n"
            "\n"
            "3. `all`: Status updates are provided and all intermediary responses are shown. "
            "Additionally, you see which response the resolver agent liked most and why (this "
            "is suppressed with `some`).\n"
        ),
    )
    parser.add_argument(
        "--model",
        required=False,
        help=(
            "(Use only for debugging. Default is GPT4 and the output scoresheet "
            "assumes you used GPT4). The name of the model you want (e.g. gpt-4, "
            "gpt-3.5-turbo)."
        ),
    )
    args = parser.parse_args()

    main(args)
