import argparse
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from smartgpt import GPTBot, Message, Mode, Role, SmartGPT, UserSettings, Verbosity
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
    return tuple(bot.response(prompt).content for bot in create_competitors(settings))


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
    grade = grader.response(get_grader_prompt(response, answer)).content

    if grade == "correct":
        return True
    elif grade == "incorrect":
        return False
    else:
        # The grader has failed to do its job. Conservatively mark incorrect
        print(f"WARNING: grader failed to produce 'correct' or 'incorrect': {grade}")
        return False


def main(args):
    settings = override_settings_with_CLI_args(UserSettings.default(), args)

    score_sheet: Dict[str, List[Any]] = {
        "subject": [],
        "question_idx": [],
        "question": [],
        "A": [],
        "B": [],
        "C": [],
        "D": [],
        "answer": [],
        "prompt": [],
        "gpt4_correct": [],
        "gpt4cot_correct": [],
        "smartgpt_correct": [],
        "gpt4_response": [],
        "gpt4cot_response": [],
        "smartgpt_response": [],
        "manually_verified": [],
    }

    questions_frame = get_questions(args.N)

    for _, question in questions_frame.iterrows():
        prompt = get_prompt(question)
        gpt, cot, smart = get_responses(prompt, settings)

        # Copy-paste some info from the question Series
        score_sheet["subject"].append(question["subject"])
        score_sheet["question_idx"].append(question["question_idx"])
        score_sheet["question"].append(question["question"])
        score_sheet["A"].append(question["A"])
        score_sheet["B"].append(question["B"])
        score_sheet["C"].append(question["C"])
        score_sheet["D"].append(question["D"])
        score_sheet["answer"].append(question["answer"])

        # Add the prompt and responses
        score_sheet["prompt"].append(prompt)
        score_sheet["gpt4_response"].append(gpt)
        score_sheet["gpt4cot_response"].append(cot)
        score_sheet["smartgpt_response"].append(smart)

        # Grade each response
        score_sheet["gpt4_correct"].append(is_correct(gpt, question["answer"]))
        score_sheet["gpt4cot_correct"].append(is_correct(cot, question["answer"]))
        score_sheet["smartgpt_correct"].append(is_correct(smart, question["answer"]))

        # Correctness has not been manually verified
        score_sheet["manually_verified"].append(False)

    score_sheet = pd.DataFrame(score_sheet)
    score_sheet.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Output TSV of scoresheet")
    parser.add_argument(
        "-N", required=True, type=int, help="The number of questions per subject"
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
