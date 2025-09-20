import subprocess
import os
import sys
import inspect
import time

space = os.getcwd()

dir_flag = False

def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)


def git_add():
    a = input('\nName to add or <Enter>\
     to \033[1;7;36madd all\033[0m, \"q\" = back\n')
    if a == "q":
        return
    if a == '':
        a = '.'
    comm = ("git add " + a)
    print(comm)
    subprocess.call(comm, shell=True)
    print('\no\'k\n')
    input('Press <Enter>')


def git_commit():
    msg = input('\nMessage (<Enter> = empty, "q" = cancel)?\n')
    if msg != 'q':
        subprocess.call(
         'git commit -m ' + '\'' + msg + ' ' + time.asctime()
         + '\'', shell=True)
        print('\no\'k\n')
        input('Press <Enter>')


def git_batch_add():
    # Get list of changed files using git status --porcelain
    proc = subprocess.Popen(['git', 'status', '--porcelain'], stdout=subprocess.PIPE, text=True)
    output, _ = proc.communicate()

    if not output.strip():
        print("\nNo changes to add.")
        input('Press <Enter>')
        return

    # Parse the list of changed files (format: XY filename)
    files = []
    for line in output.splitlines():
        # line example: " M file.py"
        # take everything after first 3 chars (status + space)
        filepath = line[3:]
        files.append(filepath)

    # Print enumerated list of changed files
    print("\nChanged files:")
    for i, f in enumerate(files, 1):
        print(f"{i}: {f}")

    print('\nEnter file numbers separated by space to add (e.g., 1 3 5),\
     or "q" to cancel:')

    while True:
        s = input('Selection: ').strip()
        if s.lower() == 'q':
            return
        if not s:
            print("Empty input, please try again.")
            continue

        try:
            indices = [int(x) for x in s.split()]
        except ValueError:
            print("Invalid input, please enter numbers separated by spaces.")
            continue

        if any(i < 1 or i > len(files) for i in indices):
            print("Some numbers are out of range, please try again.")
            continue

        # Unique chosen files
        chosen_files = sorted(set(files[i - 1] for i in indices))

        print("\nAdding files:")
        for f in chosen_files:
            print(f"  {f}")
            subprocess.call(['git', 'add', f])

        break
    #  git_commit()


def git_show():
    subprocess.call('git show', shell=True)
    print('\nEnter "q" to back\n')
    while True:
        if (input()) == 'q':
            break


def git_restore_menu():
    while True:
        mode = input('Restore from (w)orking tree or (s)taged? "q" = back\n').lower()
        if mode == 'q':
            return
        if mode in ('w', 's'):
            break
        print("Invalid choice, please enter 'w', 's', or 'q'.")

    if mode == 'w':
        print('\n\033[1;36mFiles from last commit:\033[0m\n')
        subprocess.call("git diff --name-only HEAD", shell=True)
        restore_cmd = "git restore"
        prompt_text = 'Name to restore or <Enter> to \033[1;7;36mrestore all\033[0m, "q" = back\n'
    else:
        print('\n\033[1;36mStaged files (added to index):\033[0m\n')
        subprocess.call("git diff --cached --name-only", shell=True)
        restore_cmd = "git restore --staged"
        prompt_text = 'Name to unstage or <Enter> to \033[1;7;36munstage all\033[0m, "q" = back\n'

    while True:
        a = input(prompt_text)
        if a == 'q':
            return
        if a == '':
            a = '.'
        break

    comm = f"{restore_cmd} {a}"
    print(comm)
    subprocess.call(comm, shell=True)
    print("\no'k\n")
    input('Press <Enter>')


def git_batch_action():
    """
    Unified batch action for add or restore (including staged restore)
    """
    actions = {'ba': 'add', 'br': 'restore'}
    while True:
        choice = input('\nba - batch add\nbr - batch restore\nq - back\n ').lower()
        if choice == 'q':
            return
        if choice in actions:
            action = actions[choice]
            break
        print("Invalid choice, try again.")

    files = []
    if action == 'add':
        proc = subprocess.Popen(['git', 'status', '--porcelain'], stdout=subprocess.PIPE, text=True)
        output, _ = proc.communicate()
        if not output.strip():
            input(f'\nNo changes to {action}.\nPress Enter')
            return
        for line in output.splitlines():
            files.append(line[3:])

    elif action == 'restore':
        # choose restore type
        while True:
            mode = input('Restore from (w)orking tree or (s)taged? "q" = back\n').lower()
            if mode == 'q':
                return
            if mode in ('w', 's'):
                break
            print("Invalid choice, please enter 'w', 's', or 'q'.")

        if mode == 'w':
            proc = subprocess.Popen(['git', 'diff', '--name-only', 'HEAD'], stdout=subprocess.PIPE, text=True)
            restore_cmd = 'git restore'
        else:
            proc = subprocess.Popen(['git', 'diff', '--cached', '--name-only'], stdout=subprocess.PIPE, text=True)
            restore_cmd = 'git restore --staged'

        output, _ = proc.communicate()
        files = output.splitlines()
        if not files:
            input(f'\nNo files to restore.\nPress Enter')
            return

    def print_files_in_columns(files, cols=3):
        n = len(files)
        rows = (n + cols - 1) // cols
        for r in range(rows):
            row_items = []
            for c in range(cols):
                idx = c * rows + r
                if idx < n:
                    row_items.append(f"{idx+1:3}: {files[idx]:30}")
                else:
                    row_items.append("")
            print("  ".join(row_items))

    print(f"\nChanged files:")
    print_files_in_columns(files, cols=3)
    print(f'\nEnter file numbers separated by space to {action}, or "q" to cancel:')

    while True:
        s = input('Selection: ').strip()
        if s.lower() == 'q':
            return
        if not s:
            print("Empty input, please try again.")
            continue
        try:
            indices = [int(x) for x in s.split()]
        except ValueError:
            print("Invalid input, please enter numbers separated by spaces.")
            continue
        if any(i < 1 or i > len(files) for i in indices):
            print("Some numbers are out of range, please try again.")
            continue
        chosen_files = sorted(set(files[i - 1] for i in indices))
        break

    if action == 'add':
        for f in chosen_files:
            subprocess.call(['git', 'add', f])
        msg = input('\nFile(s) added\nEnter commit message (empty to cancel): ').strip()
        if msg:
            subprocess.call(['git', 'commit', '-m', msg])
            print("\nCommit created.")
        else:
            print("Commit cancelled.")
    else:
        for f in chosen_files:
            subprocess.call(restore_cmd.split() + [f])
        print("\nRestore completed.")

    input('Press <Enter>')



def git_status():
    subprocess.call('git status', shell=True)
    print('\nEnter "q" to back\n')
    while True:
        if (input()) == 'q':
            break


def cd():
    global dir_flag
    cd = input('\nFolder: ')
    if cd == '..':
        os.chdir('..')
        dir_flag = True
    elif os.path.isdir(cd):
        os.chdir(cd)
        dir_flag = True
    else:
        input('\033[31mWrong name/address\033[0m\
        \nPlease enter correct name or Press <Enter>')


def git_init():
    subprocess.call('git init', shell=True)
    print('\no\'k\n')
    input('Press <Enter>')


menu = {
 'cd': ['change dir (<Enter> then\
 input folder name or address, .. = parent)', cd],
 'a': ['add', git_add],
 'b': ['batch action', git_batch_action],
 'c': ['commit', git_commit],
 'i': ['init', git_init],
 'r': ['restore/unsatge', git_restore_menu],
 's': ['show', git_show],
 'st': ['status', git_status],
 'q': ['quit', exit]}


while True:
    os.system('clear')
    if dir_flag:
        print(os.getcwd(), ':\n')
    else:
        print(get_script_dir(), ':\n')
    os.system('ls --color --group-directories-first')
    if '.git' in os.listdir() and os.path.isdir('.git'):
        print('\n\033[32mFound git repo\033[0m')
    else:
        print('\n\033[31mNo git repo here\033[0m')
    print()
    for x in menu:
        print((x + ' >').rjust(4), menu[x][0])
    s = input('\nAction? ')
    if s in menu:
        menu[s][1]()
