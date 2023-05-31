from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Load data
df = pd.read_csv(Path(__file__).parent / "college_physics_results.txt", sep="\t")

# Calculate mean and multiply by 100
df_mean = df[["gpt4_correct", "gpt4cot_correct", "smartgpt_correct"]].mean() * 100

# Convert the series into a DataFrame
df_mean = df_mean.reset_index()
df_mean.columns = ["variable", "value"]

# Make the plot larger
plt.figure(figsize=(5, 3.5))

# Plotting the mean values with error bars
bar_plot = sns.barplot(
    x="variable",
    y="value",
    data=df_mean,
    ci="sd",
    capsize=0.2,
    palette="hls",
    errwidth=1,
)

# Add labels
plt.title("Tests results on a 20 question college physics test")
plt.ylabel("Score (% correct)")
plt.xlabel("Model")
plt.xticks(np.arange(3), ["GPT-4", "GPT-4 CoT", "SmartGPT"])

# Set y-limit
plt.ylim(0, 100)

# Add number labels on top of bars
for index, row in df_mean.iterrows():
    bar_plot.text(index, row.value + 1, round(row.value, 2), color="black", ha="center")

plt.tight_layout()
plt.savefig(Path(__file__).parent.parent / "assets/college_physics_results.png")
