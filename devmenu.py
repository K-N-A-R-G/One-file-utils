from collections import deque
from typing import Dict, Tuple, List, Any, Callable

import traceback


RESET = "\033[0m"
BOLD = "\033[1m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RED = "\033[31m"
BLUE = "\033[34m"
CYAN = "\033[36m"

CLEAR_SCREEN = "\033[2J"
CURSOR_HOME = "\033[H"


class DevMenu:
    """
    DevMenu is a lightweight, universal CLI interactive menu system for running functions with arguments.
    Ideal for developer utilities, test consoles, and interactive tools.

    Features:
        - Create menu from a dictionary mapping keys to (description, function, args, kwargs).
        - Calls functions with arguments when selected.
        - Temporarily hides the menu while the function runs.
        - Returns to the menu after function completion or exception.
        - Logs the last messages directly in the menu (console output).

    Example usage:
        from devmenu import DevMenu

        def greet(name: str):
            print(f"Hello, {name}!")

        def add(a, b):
            print(f"{a} + {b} = {a + b}")

        actions = {
            "1": ("Say Hello", greet, ("Alice",), {}),
            "2": ("Add numbers", add, (3, 5), {}),
        }

        menu = DevMenu(actions, title="My Dev Menu")
        menu.run()

    Methods:
        __init__(actions: dict, title: str = "Dev Menu", message_lines: int = 5):
            Initializes the menu.
            actions: dict mapping keys to (description, function, args, kwargs)
            title: menu title displayed at the top
            message_lines: number of messages to show at the bottom of the menu

        run():
            Starts the menu loop.

        show_menu():
            Displays the current menu and the last messages.

        run_action(fnc: Callable, args: tuple = (), kwargs: dict = {}):
            Runs the given function in "full screen" mode, temporarily suspending the menu.
            Catches exceptions and shows traceback without breaking the menu.

        log(msg: str):
            Adds a message to the log and displays it at the bottom of the menu.
    """
    def __init__(
        self,
        actions: ActionDict,
        title: str = "Dev Menu",
        message_lines: int = 5
    ):
        self.actions = actions
        self.title = title
        self.message_lines = message_lines
        self.messages: deque[str] = deque(maxlen=message_lines)

    def show_menu(self) -> None:
        print(f"{CURSOR_HOME}{CLEAR_SCREEN}", end="")
        print(f"{BOLD}{YELLOW}=== {self.title} ==={RESET}")
        for key, (desc, fnc, args, kwargs) in self.actions.items():
            print(f"{CYAN}{key}) {desc or fnc.__name__}{RESET}")
        print(f"{CYAN}q) Quit{RESET}")
        print("\n--- Messages ---")
        # show last message_lines messages
        for msg in self.messages:
            print(msg)
        for _ in range(self.message_lines - len(self.messages)):
            print()

    def log(self, msg: str) -> None:
        self.messages.append(str(msg))
        menu_height = len(self.actions) + 5  # title + q + "--- Messages ---"
        print(f"\033[{menu_height}H", end="")
        for i, line in enumerate(self.messages):
            print(f"\033[{menu_height + i}H{line}\033[K", end="")
        for i in range(len(self.messages), self.message_lines):
            print(f"\033[{menu_height+ i}H\033[K", end="")

    def run_action(
     self,
     fnc: Callable[..., Any],
     args: Tuple[Any, ...] = (),
     kwargs: Dict[Any, Any] = {}) -> None:
        """Run function in 'full screen', temporarily suspending menu."""
        print(f"{CURSOR_HOME}{CLEAR_SCREEN}", end="")
        print(f"{BOLD}{YELLOW}=== Running {fnc.__name__} ==={RESET}\n")
        try:
            fnc(*args, **kwargs)
        except Exception as e:
            print(f"{RED}Error in {fnc.__name__}: {e}{RESET}")
            print(traceback.format_exc())
        input(f"\n{CYAN}Press Enter to return to menu...{RESET}")

    def run(self) -> None:
        while True:
            self.show_menu()
            choice = input(f"{BLUE}Choose an option: {RESET}").strip().lower()
            if choice == "q":
                self.log(f"{GREEN}Exiting menu...{RESET}")
                break
            if choice in self.actions:
                _, fnc, args, kwargs = self.actions[choice]
                self.run_action(fnc, args, kwargs)
                self.log(f"{GREEN}{fnc.__name__} finished.{RESET}")
            else:
                self.log(f"{RED}Invalid choice. Try again.{RESET}")
