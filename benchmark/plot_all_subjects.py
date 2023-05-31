from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

scoresheet = pd.read_csv(Path(__file__).parent / "all_subjects_results.txt", sep="\t")
df = (
    scoresheet.groupby("question_idx")[
        ["gpt4_correct", "gpt4cot_correct", "smartgpt_correct"]
    ]
    .mean()
    .melt()
)
df["value"] *= 100

# Make the plot larger
plt.figure(figsize=(5, 3.5))

# Plotting all the values as dots
sns.stripplot(x="variable", y="value", data=df, jitter=True, color="black")

# Plotting the mean values with error bars
sns.barplot(
    x="variable", y="value", data=df, ci="sd", capsize=0.2, palette="hls", errwidth=1
)

# Add labels
plt.title("Mean scores for 57-subject testing\n(1 question per subject)")
plt.ylabel("Score (% correct)")
plt.xlabel("Model")
plt.xticks(np.arange(3), ["GPT-4", "GPT-4 CoT", "SmartGPT"])

plt.ylim(df.value.min() - 1, df.value.max() + 1)

plt.tight_layout()
plt.savefig(Path(__file__).parent.parent / "assets/all_subjects.png")
