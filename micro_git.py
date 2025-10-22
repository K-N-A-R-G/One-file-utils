import subprocess
import os
import sys
import inspect
import shutil
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
    Supports automatic .gitchosen usage.
    """
    actions = {'ba': 'add', 'br': 'restore'}

    # --- integrate .gitchosen awareness ---
    chosen_list = None
    if os.path.exists(".gitchosen"):
        print("\n\033[32mDetected .gitchosen file.\033[0m")
        use = input("Use saved selection from .gitchosen? [y/N/v] ").strip().lower()
        if use == "v":
            os.system("${EDITOR:-nano} .gitchosen")
            use = input("Use updated .gitchosen now? [y/N] ").strip().lower()
        if use == "y":
            with open(".gitchosen", "r", encoding="utf-8") as f:
                chosen_list = [x.strip() for x in f if x.strip()]
            print(f"\nUsing {len(chosen_list)} files from .gitchosen.\n")

    # choose an action
    while True:
        choice = input('\nba - batch add\nbr - batch restore\nq - back\n ').lower()
        if choice == 'q':
            return
        if choice in actions:
            action = actions[choice]
            break
        print("Invalid choice, try again.")

    # If .gitchosen is selected, execute immediately, without manual selection
    if chosen_list is not None:
        chosen_list = [f for f in chosen_list if os.path.exists(f)]
        if not chosen_list:
            print("No valid files in .gitchosen.")
            input("Press <Enter>")
            return

        if action == 'add':
            print(f"\nAdding {len(chosen_list)} file(s) from .gitchosen...\n")
            for f in chosen_list:
                subprocess.call(['git', 'add', f])
            msg = input('\nEnter commit message (empty to cancel): ').strip()
            if msg:
                subprocess.call(['git', 'commit', '-m', msg])
                print("\nCommit created.")
            else:
                print("Commit cancelled.")
        else:
            print(f"\nRestoring {len(chosen_list)} file(s) from .gitchosen...\n")
            restore_cmd = 'git restore'
            for f in chosen_list:
                subprocess.call(restore_cmd.split() + [f])
            print("\nRestore completed.")
        input('Press <Enter>')
        return

    # standard logic if .gitchosen is not used
    files = []
    if action == 'add':
        proc = subprocess.Popen(['git', 'status', '--porcelain'],
                                stdout=subprocess.PIPE, text=True)
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
            proc = subprocess.Popen(['git', 'diff', '--name-only', 'HEAD'],
                                    stdout=subprocess.PIPE, text=True)
            restore_cmd = 'git restore'
        else:
            proc = subprocess.Popen(['git', 'diff', '--cached', '--name-only'],
                                    stdout=subprocess.PIPE, text=True)
            restore_cmd = 'git restore --staged'

        output, _ = proc.communicate()
        files = output.splitlines()
        if not files:
            input('\nNo files to restore.\nPress Enter')
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

    print("\nChanged files:")
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


def git_choose():
    """
    Interactive .gitchosen editor: select/unselect files visually.
    """
    chosen_path = ".gitchosen"

    def load_chosen():
        if not os.path.exists(chosen_path):
            return set()
        with open(chosen_path, "r", encoding="utf-8") as f:
            return set(x.strip() for x in f if x.strip())

    def save_chosen(chosen):
        with open(chosen_path, "w", encoding="utf-8") as f:
            for f_ in sorted(chosen):
                f.write(f_ + "\n")

    def clear_screen():
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    def move_cursor(y, x):
        sys.stdout.write(f"\033[{y};{x}H")

    # collect all files except .git/
    files = []
    for root, _, names in os.walk(".", topdown=True):
        if ".git" in root:
            continue
        for n in names:
            files.append(os.path.relpath(os.path.join(root, n), "."))

    files.sort()
    chosen = load_chosen()

    while True:
        clear_screen()
        print(f"\033[1;36mInteractive chooser (.gitchosen)\033[0m\n")
        for i, f in enumerate(files, 1):
            mark = "\033[32m✓\033[0m" if f in chosen else " "
            print(f"{i:3}: [{mark}] {f}")

        print("\nEnter numbers (toggle), 'v' to edit file, 'q' to exit.")
        s = input("Selection: ").strip()
        if s.lower() == "q":
            break
        if s.lower() == "v":
            os.system(f"${{EDITOR:-nano}} {chosen_path}")
            chosen = load_chosen()
            continue

        try:
            indices = [int(x) for x in s.split()]
        except ValueError:
            continue

        for i in indices:
            if 1 <= i <= len(files):
                f = files[i - 1]
                if f in chosen:
                    chosen.remove(f)
                else:
                    chosen.add(f)

        save_chosen(chosen)

    clear_screen()
    print(f"\nSaved {len(chosen)} selected files to {chosen_path}.")
    input("Press <Enter>")



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


def autostage_gitchosen():
    """
    Auto-check .gitchosen at program start and offer quick add/commit
    (compact mode — shows count, details on 'v')
    """
    if not os.path.exists(".gitchosen"):
        return

    proc = subprocess.Popen(["git", "status", "--porcelain"],
                            stdout=subprocess.PIPE, text=True)
    output, _ = proc.communicate()
    changed = {line[3:].strip() for line in output.splitlines() if len(line) > 3}

    if not changed:
        return

    with open(".gitchosen", "r", encoding="utf-8") as f:
        chosen = [x.strip() for x in f if x.strip()]

    affected = [f for f in chosen if f in changed]
    if not affected:
        return

    count = len(affected)
    print(f"\n\033[33m{count} changed file(s) from .gitchosen detected.\033[0m")

    ans = input("Add them now? [y/N/\033[1mv\033[2miew] ").strip().lower()
    if ans == "v":
        print("\n\033[36mAffected files:\033[0m")
        for i, f in enumerate(affected, 1):
            print(f" {i:2}) {f}")
        ans = input("\nAdd them now? [y/n] ").strip().lower()

    if ans != "y":
        return

    for f in affected:
        subprocess.call(["git", "add", f])
    print(f"\nAdded {count} file(s).")

    msg = input("Enter commit message (empty = skip): ").strip()
    if msg:
        subprocess.call(["git", "commit", "-m", msg])
        print("\nCommit created.")
    else:
        print("Commit skipped.")

    input("Press <Enter> to continue...")


autostage_gitchosen()

menu = {
 'cd': ['change dir (<Enter> then\
 input folder name or address, .. = parent)', cd],
 'a': ['add', git_add],
 'b': ['batch action', git_batch_action],
 'c': ['commit', git_commit],
 'ch': ['choose files (.gitchosen)', git_choose],
 'i': ['init', git_init],
 'r': ['restore/unsatge', git_restore_menu],
 's': ['show', git_show],
 'st': ['status', git_status],
 'q': ['quit', exit]}


while True:
    os.system('clear')
    # if dir_flag:
    print(os.getcwd(), ':\n')
    # else:
        # print(get_script_dir(), ':\n')
    os.system('ls --color --group-directories-first')
    if '.git' in os.listdir() and os.path.isdir('.git'):
        print('\n\033[32mFound git repo\033[0m')
    else:
        print('\n\033[31mNo git repo here\033[0m')
    if os.path.exists('.gitchosen'):
        print('\033[32mFound .gitchosen\033[0m — use via "ch" or in batch ops\033[0m\n')

    for x in menu:
        print((x + ' >').rjust(4), menu[x][0])
    s = input('\nAction? ')
    if s in menu:
        menu[s][1]()
