from pathlib import Path
from typing import List

prompts = {
    path.stem: open(path).read().strip() for path in Path(__file__).parent.glob("*.txt")
}


def step_by_step(prompt: str) -> str:
    return prompts["step_by_step"].format(prompt=prompt)


def you_are_a_researcher(question: str, candidates: List[str]) -> str:
    answers = []
    for idx, candidate in enumerate(candidates):
        answers.append(f"Option {idx+1}: {candidate}")

    return prompts["researcher"].format(
        N=len(candidates),
        answer_list="\n\n".join(answers),
    )


def you_are_a_resolver() -> str:
    return prompts["resolver"]
