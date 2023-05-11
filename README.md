# SmartGPT

SmartGPT as explained in this video by AIExplained: https://www.youtube.com/watch?v=wVzuvf9D9BU

## Installation

<details><summary">Install option (1): PIP</summary>
FIXME
</details>


<details><summary>Install option (3): Developer</summary>

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
export PATH=\$PATH:$(pwd)
EOF
```

The next time you activate your conda environment (`conda activate smartgpt`), `run_smartgpt` (or `run_smartgpt.bat` if you're on Windows) is now a binary that can be run anywhere in your filesystem whenever you are in the `smartgpt` conda environment. Test it out:

```
conda activate smartgpt
cd ~
run_smartgpt
```

</details>
