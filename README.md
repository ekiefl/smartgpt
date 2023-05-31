# SmartGPT

<img src="assets/alg.jpg"/>

SmartGPT uses a collection of GPT-4 agents, each with specific roles, to produce demonstrably higher quality responses than vanilla GPT-4. It also leverages chain-of-thought prompt engineering to boost performance.

SmartGPT was conceived by AIExplained in his video: https://www.youtube.com/watch?v=wVzuvf9D9BU.

## Is it really better? (yes)

### All subjects

<img src="assets/all_subjects.png"/>

[Here is the scoresheet](https://github.com/ekiefl/smartgpt/blob/eb3a362176e4177a3b2e91f8af905f95a025c2ce/benchmark/all_subjects_results.txt)

Above are the results from three independent tests, where each test is composed of 57 questions, each from a distinct subject matter (from the MMLU test suite). I couldn't afford the number of tokens that would be required to prove statistical significance, however **if people want to donate their API keys, I'm happy to continue the experiment**.

Overall, it is quite impressive, where **in one case SmartGPT scored 91% on a 57 question all-subjects exam**.

Now diving into individual subject matters.

### College physics

<img src="assets/college_physics_results.png"/>

[Here is the scoresheet](https://github.com/ekiefl/smartgpt/blob/eb3a362176e4177a3b2e91f8af905f95a025c2ce/benchmark/college_physics_results.txt)

Above are the results of a 20-question college-level physics exam (again, taken form the MMLU test suite). SmartGPT absolutely hammers it home with 90%, versus 65% for vanilla GPT-4. I have manually verified each answer. I don't know what else to say here but wow.

### Formal logic

TODO

### Response quality is superior

It is also important to consider the quality of answers, even when all models get the question right. For example consider the question:

>_Find all zeros in the indicated finite field of the given polynomial with coefficients in that field. x^5 + 3x^3 + x^2 + 2x in Z_5.  
A. 0  
B. 1  
C. 0,1  
D. 0,4_

GPT-4 response:

> D. 0,4

SmartGPT response:

> First, recall that Z_5 is the finite field with 5 elements {0, 1, 2, 3, 4}, and addition and multiplication are performed modulo 5. We want to find the zeros (roots) of the polynomial x^5 + 3x^3 + x^2 + 2x in Z_5, that is, we want to find all the elements a in Z_5 such that f(a) = 0, where f(x) = x^5 + 3x^3 + x^2 + 2x.
> 
> Let's test each element of Z_5:
> 
> 1. For x = 0:
> f(0) = 0^5 + 3(0)^3 + (0)^2 + 2(0) = 0. So 0 is a root.
> 
> 2. For x = 1:
> f(1) = 1^5 + 3(1)^3 + (1)^2 + 2(1) = 1 + 3 + 1 + 2 = 7 ‚â° 2 (mod 5). 1 is not a root.
> 
> 3. For x = 2:
> f(2) = 2^5 + 3(2)^3 + (2)^2 + 2(2) = 32 + 3(8) + 4 + 4 ‚â° 32 + 24 + 8 (mod 5) ‚â° 64 (mod 5) ‚â° 4 (mod 5). 2 is not a root.
> 
> 4. For x = 3:
> f(3) = 3^5 + 3(3)^3 + (3)^2 + 2(3) = 243 + 3(27) + 9 + 6 ‚â° 243 + 81 + 15 (mod 5) ‚â° 339 (mod 5) ‚â° 4 (mod 5). 3 is not a root.
> 
> 5. For x = 4:
> f(4) = 4^5 + 3(4)^3 + (4)^2 + 2(4) = 1024 + 3(64) + 16 + 8 ‚â° 1024 + 192 + 24 (mod 5) ‚â° 1240 (mod 5) ‚â° 0 (mod 5). 4 is a root.
> 
> So the zeros of the polynomial in Z_5 are 0 and 4.
> 
> Answer: D. 0, 4

## Explanation of the algorithm

In essence, SmartGPT works by generating a diversity of responses to a prompt, and then scrutinizing and improving these responses via agents with dedicated roles.

There are currently 3 agent roles: **Generators**, **Reseachers**, and **Resolvers**.

- **Generators** produce zero-shot responses to a prompt (with chain-of-thought prompt wrappings).

- **Researchers** take in collections of generator responses as part of their prompt, and are tasked with identifying the strengths and weaknesses of the responses.

- **Resolvers** take the analysis of a researcher as their prompt, and are tasked with choosing and improving upon the best option.

The prompts for each of these agent types can be found in `smartgpt/prompts`

There is nothing but your creativity preventing a vast expansion of more tailored roles.

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
