#!/usr/bin/env python3
"""
Directory Tree Generator

This script generates a directory tree of the specified folder,
printing the structure to the terminal and/or saving it to a file.

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
"""
import argparse
import os
import sys

def tree(
         dir_path: str,
         prefix: str = "",
         show_hidden: bool = False
         ) -> list[str]:
    entries = sorted(e for e in os.listdir(dir_path)
    if show_hidden or not e.startswith("."))
    lines = []
    entries_count = len(entries)
    for i, entry in enumerate(entries):
        path = os.path.join(dir_path, entry)
        connector = "└── " if i == entries_count - 1 else "├── "
        lines.append(prefix + connector + entry)
        if os.path.isdir(path):
            extension = "    " if i == entries_count - 1 else "│   "
            lines.extend(tree(path, prefix + extension))
    return lines

def interactive_mode():
    folder = input("Choose folder (default: current): ").strip() or os.getcwd()
    if not os.path.isdir(folder):
        print("Invalid folder path.")
        return
    file_out = input(
    "Filename for output (empty = no save, 'd' = default 'tree.txt'): ").strip()
    if file_out == "":
        file_out = None
    elif file_out == "d":
        file_out = "tree.txt"
    show_hidden = input("Show hidden files/folders? (y/N): ").strip().lower() == "y"
    return folder, file_out, show_hidden

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

    if len(sys.argv) == 1:
        print("[Info] No arguments provided. Entering interactive mode.\n")
        args = parser.parse_args(["--interactive"])
    else:
        args = parser.parse_args()

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
    lines = tree(folder, show_hidden=show_hidden)

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

