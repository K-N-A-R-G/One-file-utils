#!/usr/bin/env python3
"""
Directory Tree Generator with Ignore List Support

This script generates a directory tree of the specified folder,
printing the structure to the terminal and/or saving it to a file.

It supports ignoring specified directories by name, either by
providing them at runtime or loading/saving them from/to a .treeignore file
located in the root folder.

Usage:

  python3 make_tree.py [options] [folder]

Where:
  folder           — root directory path (default: current directory)

Options:
  -i, --interactive
      Run in interactive mode to choose folder and output file

  -s, --silent
      Do not print the tree to the terminal (output to file only)

  -o FILE, --output FILE
      Output filename (default: "tree.txt")

Examples:

  python3 make_tree.py
      Generate tree for current folder, print to terminal and save to tree.txt

  python3 make_tree.py -s -o mytree.txt /home/user
      Generate tree for /home/user, no terminal output, save to mytree.txt

  python3 make_tree.py -i
      Run interactive mode to select folder and output file

Note:
  In silent mode (-s), specifying an output file (-o) is mandatory;
  otherwise the script will exit with an error.

Additional features:
  - Supports directory ignore list via .treeignore file in root folder.
  - On startup, if .treeignore exists, allows using it, ignoring it,
    or creating a new ignore list.
  - Allows specifying ignore directories interactively if no .treeignore found.
"""

import argparse
import difflib
import os
import sys


def tree(
         dir_path: str,
         prefix: str = "",
         show_hidden: bool = False,
         ignore_names: set[str] = None
         ) -> list[str]:
    if ignore_names is None:
        ignore_names = set()
    entries = sorted(e for e in os.listdir(dir_path)
                     if (show_hidden or not e.startswith("."))
                     and e not in ignore_names)
    lines = []
    entries_count = len(entries)
    for i, entry in enumerate(entries):
        path = os.path.join(dir_path, entry)
        connector = "└── " if i == entries_count - 1 else "├── "
        lines.append(prefix + connector + entry)
        if os.path.isdir(path):
            extension = "    " if i == entries_count - 1 else "│   "
            lines.extend(tree(path, prefix + extension, show_hidden, ignore_names))
    return lines


def compare_trees(lines_old: list[str], lines_new: list[str]):
    for line in difflib.ndiff(lines_old, lines_new):
        if line.startswith("+ "):
            print("\033[32m" + line + "\033[0m")  # green
        elif line.startswith("- "):
            print("\033[2;34m" + line + "\033[0m")  # dim blue
        else:
            print(line)


def interactive_mode():
    while True:
        print("\n--- Directory Tree Tool ---")
        print("1. Generate tree")
        print("2. Compare saved trees")
        print("0. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            folder = input("Choose folder (default: current): ").strip() or os.getcwd()
            if not os.path.isdir(folder):
                print("Invalid folder path.")
                continue

            file_out = input("Filename for output (empty = no save, default 'tree.txt'): ").strip()
            if file_out.lower() == "none" or file_out == "":
                file_out = None
            elif file_out is None:
                file_out = "tree.txt"

            show_hidden = input("Show hidden files/folders? (y/N): ").strip().lower() == "y"
            return folder, file_out, show_hidden

        elif choice == "2":
            files = input(
                "Enter one filename to compare with current directory (default: tree.txt),\n"
                "or two filenames to compare them directly:\n> "
            ).strip().split()

            if not files:
                files = ["tree.txt"]

            if len(files) == 1:
                filepath = files[0]
                if not os.path.isfile(filepath):
                    print(f"Error: File '{filepath}' not found.")
                    continue
                with open(filepath, encoding="utf-8") as f:
                    lines_saved = [line.rstrip("\n") for line in f.readlines()]
                show_hidden = input("Show hidden files/folders? (y/N): ").strip().lower() == "y"
                root_name = os.path.basename(os.getcwd()) or "."
                lines_current = [root_name + "/"] + tree(os.getcwd(), show_hidden=show_hidden)
                compare_trees(lines_saved, lines_current)

            elif len(files) == 2:
                f1, f2 = files
                if not all(os.path.isfile(f) for f in (f1, f2)):
                    print("Error: One or both files do not exist.")
                    continue
                with open(f1, encoding="utf-8") as a, open(f2, encoding="utf-8") as b:
                    lines1 = [line.rstrip("\n") for line in a.readlines()]
                    lines2 = [line.rstrip("\n") for line in b.readlines()]
                compare_trees(lines1, lines2)

            else:
                print("Error: Please provide at most two filenames.")

        elif choice == "0":
            return

        else:
            print("Invalid option.")


def load_treeignore(root_folder: str) -> set[str] | None:
    path = os.path.join(root_folder, ".treeignore")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return set(lines)


def save_treeignore(root_folder: str, ignore_list: list[str]):
    path = os.path.join(root_folder, ".treeignore")
    # добавляем '.treeignore' в список, если его нет
    if ".treeignore" not in ignore_list:
        ignore_list = ignore_list + [".treeignore"]
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Files and directories to ignore, one per line\n")
        for d in ignore_list:
            f.write(d + "\n")


def prompt_ignore_list(root_folder: str) -> set[str]:
    existing_ignore = load_treeignore(root_folder)
    if existing_ignore is not None:
        print(f"Found .treeignore in {root_folder} with exclusions:")
        for d in existing_ignore:
            print(f"  {d}")
        print("Choose: 1 - use these exclusions and continue")
        print("        2 - ignore .treeignore and continue without exclusions")
        print("        3 - create new exclusions list")
        while True:
            choice = input("Your choice [1/2/3]: ").strip()
            if choice == "1":
                return existing_ignore
            elif choice == "2":
                return set()
            elif choice == "3":
                break
            else:
                print("Invalid input")
    else:
        print(f"No .treeignore found in {root_folder}.")

    # Create new list
    ignore_input = input("Enter space-separated files/directories to ignore (empty = none): ").strip()
    if ignore_input:
        ignore_names = set(ignore_input.split())
        save = input("Save these exclusions to .treeignore? (y/N): ").strip().lower()
        if save == "y":
            save_treeignore(root_folder, sorted(ignore_names))
            print(".treeignore saved.")
        return ignore_names
    return set()


def main():
    parser = argparse.ArgumentParser(description="Directory tree script")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Run script in interactive mode")
    parser.add_argument("-s", "--silent", action="store_true",
                        help="Do not print tree to terminal")
    parser.add_argument(
        "-o", "--output", nargs="?", const="tree.txt",
        help="Save output to file (default: tree.txt). Use 'none' to disable saving."
    )
    parser.add_argument("--show-hidden", action="store_true",
                        help="Include hidden files and directories")
    parser.add_argument("folder", nargs="?", default=os.getcwd(),
                        help="Root folder to build tree from (default: current directory)")
    parser.add_argument(
        "--compare", nargs="+", metavar="FILE", type=str,
        help=(
            "Compare saved trees: one file (vs current directory) or two files. "
            "Differences will be printed in color. Hidden files respected only if --show-hidden is set."
        )
    )
    parser.add_argument(
    "--ignore",
    action="store_true",
    help="Automatically use .treeignore file if present in the root folder,\
     without prompting"
    )

    if len(sys.argv) == 1:
        print("[Info] No arguments provided. Entering interactive mode.\n")
        args = parser.parse_args(["--interactive"])
    else:
        args = parser.parse_args()

    if args.compare:
        files = args.compare
        if len(files) == 1:
            filepath = files[0]
            if not os.path.isfile(filepath):
                print(f"Error: File '{filepath}' not found.")
                return
            with open(filepath, encoding="utf-8") as f:
                lines_saved = [line.rstrip("\n") for line in f.readlines()]
            root_name = os.path.basename(os.getcwd()) or "."
            lines_current = [root_name + "/"] + tree(os.getcwd(), show_hidden=args.show_hidden)
            compare_trees(lines_saved, lines_current)

        elif len(files) == 2:
            f1, f2 = files
            if not all(os.path.isfile(f) for f in (f1, f2)):
                print("Error: One or both files do not exist.")
                return
            with open(f1, encoding="utf-8") as a, open(f2, encoding="utf-8") as b:
                lines1 = [line.rstrip("\n") for line in a.readlines()]
                lines2 = [line.rstrip("\n") for line in b.readlines()]
            compare_trees(lines1, lines2)

        else:
            print("Error: --compare requires one or two file paths.")
        return

    if args.interactive:
        result = interactive_mode()
        if not result:
            return
        folder, file_out, show_hidden = result
        silent = False
    else:
        folder = args.folder
        silent = args.silent
        show_hidden = args.show_hidden

        # interpret `-o` option
        if args.output == "none":
            file_out = None
        elif args.output is not None:
            file_out = args.output  # either filename or default 'tree.txt'
        else:
            file_out = None  # no output unless explicitly set

        if silent and not file_out:
            print("Error: Silent mode requires output file (-o or default)")
            return

    root_name = os.path.basename(folder) or folder

    if args.ignore:
        ignore_names = load_treeignore(folder)
        if ignore_names is None:
            ignore_names = set()
    else:
        ignore_names = prompt_ignore_list(folder)
    lines = tree(folder, show_hidden=show_hidden, ignore_names=ignore_names)

    if not silent:
        print(root_name + os.sep)
        for line in lines:
            print(line)

    if file_out:
        with open(file_out, "w", encoding="utf-8") as f:
            f.write(f"{root_name}{os.sep}\n")
            f.write("\n".join(lines))
            f.write("\n")
        if not silent:
            print(f"\nSaved tree to {file_out}")


if __name__ == "__main__":
    main()
