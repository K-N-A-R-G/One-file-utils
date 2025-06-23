# One-file-utils
## Small applications for the daily needs of the developer.

### _Table of contains_:
- [_micro-git_](#micro-git)
- [_halt_](#halt)
- [_make_tree_](#make_tree)
---

# micro-git

**A minimalist CLI tool for fast and convenient Git operations**

`micro-git` is a small Python script that allows quick execution of basic Git commands (add, commit, batch add/commit, status, etc.) from the console with a simple text menu.
It’s perfect for local use in projects with frequent commits.

![expample](images/micro_git_1.png)
![expample](images/micro_git_2.png)
![expample](images/micro_git_3.png)

---

## Key Features

- Automatically detects the script’s own location and the current working directory
- Auto-detects `.git` folder in the current directory
- Add individual files or all at once
- Batch add and commit selected files
- View Git status and recent changes (`git status`, `git show`)
- Navigate directories from the menu
- Initialize a new Git repository

**Unique feature:**
The script detects its own location intentionally so that this single small file can be moved or copied into any project folder and run right from there — no need to `cd` into the directory first, saving you time and effort.

---

## Installation

1. Download the `micro_git.py` file to a convenient location, for example, `~/bin/`
2. Make it executable:

```bash
chmod +x ~/bin/micro_git.py
```
3. Run it from the console:
```bash
~/bin/micro_git.py
```
You can also place this file directly inside your project folder and run it simply from the IDE. Keep in mind that some IDEs, such as Pycharm, have problems executing ANSI codes (colored text, positioning, etc) in their virtual terminal.

## Usage
After launching, the script will show a menu with available actions, for example:
Select an action by entering the corresponding letter and follow the prompts.

Example: Batch Add and Commit
- Choose b — batch action

- Choose ba — batch add & commit

The script will display a list of changed files with numbers

- Enter the numbers of the files you want to add, separated by spaces (e.g., 1 3 5), or press Enter to add all

- Enter the commit message

- Receive confirmation of a successful commit
---

# halt
## Timing and Argument Inspection Module

**`halt`** is a lightweight utility module for measuring the execution time of a function, either by using it as a **decorator** or by calling it **explicitly**. It also provides introspection on the parameters and arguments passed to the function.

![example](images/halt.png)
---

## Features

- Measure execution time of any function.
- Inspect full parameter/argument mapping.
- Can be used as a decorator or a function call.
- Returns the result of the original function.
- Works as a **single-file utility**, ready to be dropped into any folder and used immediately without changing directories.

---

## ⚠️ Important Limitation

> **Do not use `halt` as both a decorator and a callable wrapper on the same function.**
> This will cause infinite recursion and crash with a `RecursionError`.

---
## Installation
> Place the file `halt.py` in the folder where your project files are found. Or, a more universal solution: place this file inside `/lib` or `/site-packages` inside your Python. Then simply import to your code.

---
## Usage

### 1. As a decorator (for measuring execution time only)

```python
from halt import halt
from time import sleep


@halt
def slow(n: int | float=0):
    sleep(n)
    print('Done\n')


slow(0.7)
```

### 2. As a callable wrapper

```python
from halt import halt
from time import sleep


def slow(n: int | float=0):
    sleep(n)
    print('Done\n')


halt.time(0.5, fnc=slow)
halt.params(0.33, fnc=slow)
```

### 3. More complicated use when wrapping in `halt` does not interfere with the implementation of the main logic of code

```python
from halt import halt
from time import sleep


def adder(
 a: int | float,
 b: int | float) -> int | float:
    sleep(0.5)
    return a + b


print(halt.time(8, 31, fnc=adder) * halt.params(0.3, 2.7, fnc=adder))
```

```python
from halt import halt
from time import sleep


@halt
def adder(
 a: int | float,
 b: int | float) -> int | float:
    sleep(0.5)
    return a + b


print(adder(13, 22) / adder(0.3, 3.3))
```
---
# make_tree
## Directory Tree Generator

A simple Python script to generate a directory tree structure
for a specified folder, printing it to the terminal and/or saving
to a text file.

---

## Features

- Recursively lists all files and folders, including hidden ones
- Outputs a classic tree structure with `├──`, `│`, and `└──` characters
- Interactive mode for choosing folder and output file
- Command-line options to control input folder, output file, and verbosity

---

## Usage

```bash
python3 make_tree.py [options] [folder]
```
