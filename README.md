# SmartGPT

<img src="assets/alg.jpg"/>

SmartGPT uses a collection of GPT-4 agents, each with specific roles, to produce demonstrably higher quality responses than vanilla GPT-4. It also leverages chain-of-thought prompt engineering to boost performance.

SmartGPT was conceived by AIExplained in his video: https://www.youtube.com/watch?v=wVzuvf9D9BU.

## Explanation of the algorithm

In essence, SmartGPT works by generating a diversity of responses to a prompt, and then scrutinizing and improving these responses via agents with dedicated roles.

There are currently 3 agent roles: **Generators**, **Reseachers**, and **Resolvers**.

- **Generators** produce zero-shot responses to a prompt (with chain-of-thought prompt wrappings).

- **Researchers** take in collections of generator responses as part of their prompt, and are tasked with identifying the strengths and weaknesses of the responses.

- **Resolvers** take the analysis of a researcher as their prompt, and are tasked with choosing and improving upon the best option.

The prompts for each of these agent types can be found in `smartgpt/prompts`

There is nothing but your creativity preventing a vast expansion of more tailored roles.

## Is it really better? (yes)

FIXME

## Requirements

- Python >=3.8

## Installation

The easiest way to install SmartGPT is with pip:

```bash
pip install smartgpt
```

If you want to develop for SmartGPT, you'll want to follow these instructions (click the arrow to expand):

<details><summary>Install option (2): Developer</summary>

**(i)** create a new, python environment that uses Python 3.8.10.

With `conda`, you could do the following:

```bash
conda deactivate
conda env remove --name smartgpt
conda create -y -n smartgpt python=3.8.10
conda activate smartgpt
```

Regardless of how you managed your python environment, please verify you're running `3.8.10`

```
$ python
Python 3.8.10 (default, May 19 2021, 11:01:55)
[Clang 10.0.0 ] :: Anaconda, Inc. on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> exit()
```

**(ii)** grab the codebase:

```bash
cd <A_DIRECTORY_YOU_LIKE>
git clone https://github.com/ekiefl/smartgpt.git
cd smartgpt
```

**(iii)** install the dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

In addition to `requirements.txt`, `requirements-dev.txt` includes some modules required for developement.

Install the pre-commit hooks. This will automatically format your code:

```
pre-commit install
```

**(iv)** if you used a conda environment that you named `smartgpt`, create this script that runs whenever the conda environment is activated. This script modifies `$PATH` and `$PYTHONPATH` so that python knows where to find smartgpt libraries and the shell knows where to find the smartgpt binary. **These path modifications live safely inside the smartgpt conda environment, and do not propagate into your global
environment**:

(_This is a multi-line command. Paste the entire block into your command line prompt._)

```
mkdir -p ${CONDA_PREFIX}/etc/conda/activate.d
cat <<EOF >${CONDA_PREFIX}/etc/conda/activate.d/smartgpt.sh
export PYTHONPATH=\$PYTHONPATH:$(pwd)
export PATH=\$PATH:$(pwd)/bin
EOF
```

The next time you activate your conda environment (`conda activate smartgpt`), `run_smartgpt` (or `run_smartgpt.bat` if you're on Windows) is now a binary that can be run anywhere in your filesystem whenever you are in the `smartgpt` conda environment. Test it out:

```
conda activate smartgpt
cd ~
run_smartgpt
```

</details>

## Usage

SmartGPT can be ran from the command line or directly in Python.

### From the command line

After installing, you now have a binary in your `$PATH` called `smartgpt`. This binary creates a REPL where you can interactively chat with the model in zero-shot mode, basic chain-of-through prompt wrapping, or the SmartGPT algorithm.

Definitely run the following command to help you get started. It will guide you through everything you need to know.

```bash
smartgpt --help
```

### From the python API

If you have more programmatic intentions, I hope the following scripts give you some inspiration.

Talk with a normal GPT bot:

```python
>>> from smartgpt import GPTBot
>>> bot = GPTBot()
>>> bot.response("Hello there")
Message(role=<Role.ASSISTANT: 'assistant'>, content='Hello! How can I help you today?')
>>> bot
GPTBot(messages=[{'role': <Role.USER: 'user'>, 'content': 'Hello there'}, {'role': <Role.ASSISTANT: 'assistant'>, 'content': 'Hello! How can I help you today?'}], credentials=Credentials(key=sk-r****v9t6), model='gpt-4', temp=0.5)
```

Talk with SmartGPT bots:

```python
from smartgpt import SmartGPT, Mode

# Same as `GPTBot()`
dumb_bot = SmartGPT.create(mode=Mode.ZERO_SHOT)

# Use chain-of-thought prompt engineering
smart_bot = SmartGPT.create(mode=Mode.STEP_BY_STEP)

# Use the SmartGPT implementation
smartest_bot = SmartGPT.create(mode=Mode.RESOLVER)

prompt = "How many shoes can fit in a house?"

dumb_bot.response(prompt)
smart_bot.response(prompt)
smartest_bot.response(prompt)
```
