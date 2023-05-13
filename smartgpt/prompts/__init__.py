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
        answers.append(f"Answer option {idx+1}:\n\n{candidate}")

    return prompts["researcher"].format(
        N=len(candidates),
        question=question,
        answer_list="\n\n".join(answers),
    )


def you_are_a_resolver(candidates: List[str]) -> str:
    return prompts["resolver"].format(N=len(candidates))
