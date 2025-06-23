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
import os
import argparse

def tree(dir_path: str, prefix: str = "") -> list[str]:
    entries = sorted(os.listdir(dir_path))
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
    folder = input(f"Choose folder (default current): ").strip() or os.getcwd()
    if not os.path.isdir(folder):
        print("Invalid folder path.")
        return
    file_out = input("Filename for output (empty = no save, default 'tree.txt'): ").strip()
    if file_out == "":
        file_out = None
    elif file_out is None:
        file_out = "tree.txt"
    return folder, file_out

def main():
    parser = argparse.ArgumentParser(description="Directory tree script")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Run script in interactive mode")
    parser.add_argument("-s", "--silent", action="store_true",
                        help="Do not print tree to terminal")
    parser.add_argument("-o", "--output", type=str, default="tree.txt",
                        help="Output filename (default: tree.txt)")
    parser.add_argument("folder", nargs="?", default=os.getcwd(),
                        help="Root folder to build tree from (default: current directory)")

    args = parser.parse_args()

    if args.interactive:
        result = interactive_mode()
        if not result:
            return
        folder, file_out = result
        silent = False
    else:
        folder = args.folder
        silent = args.silent
        # если silent, файл обязателен, если не указан, дефолт "tree.txt"
        file_out = args.output if not silent or args.output else None
        if silent and not file_out:
            print("Silent mode requires output file specified with -o")
            return

    root_name = os.path.basename(folder) or folder
    lines = tree(folder)

    if not silent:
        print(root_name + "/")
        for line in lines:
            print(line)

    if file_out:
        with open(file_out, "w", encoding="utf-8") as f:
            f.write(root_name + "/\n")
            f.write("\n".join(lines))
            f.write("\n")
        if not silent:
            print(f"\nSaved tree to {file_out}")

if __name__ == "__main__":
    main()

