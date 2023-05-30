from pathlib import Path

import pandas as pd

QUESTIONS_DIR = Path(__file__).parent / "questions"

_col_names = ["question", "A", "B", "C", "D", "answer"]

tests = {
    path.stem[: -len("_test")]: pd.read_csv(path, names=_col_names).assign(
        subject=path.stem[: -len("_test")]
    )
    for path in QUESTIONS_DIR.glob("*.csv")
}


def _format_subject(subject: str) -> str:
    return subject.replace("_", " ")


def get_prompt(question: pd.Series) -> str:
    prompt = (
        f"Please choose the most correct answer for the following multiple choice "
        f"question about {_format_subject(question['subject'])}. Clearly indicate "
        f"your selected option (A, B, C, or D) at the end of your response. "
        f"{question['question']}\n\n"
    )

    for option in ["A", "B", "C", "D"]:
        prompt += f"{option}. {question[option]}\n"

    return prompt
