from collections import deque
from pathlib import Path
from typing import Tuple, Dict, List, Any, Optional, Callable, Union

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

MenuNode = Tuple[str, Callable[..., Any], Tuple[Any, ...], Dict[Any, Any]]
ActionDict = Dict[str, MenuNode]

class DevMenu:
    """
    DevMenu — a lightweight, node-style action router for running functions with
    arguments. It can operate either as an interactive CLI menu or as a fully
    programmatic dispatcher (auto-mode).

    ----------------------------------------------------------------------
    Concept
    ----------------------------------------------------------------------
    A DevMenu is built from a dictionary:

        key -> (description, function, args, kwargs)

    In interactive mode, the menu is rendered in the terminal and the user selects
    actions manually.

    In auto-mode (auto=True), DevMenu does not display anything, does not wait for
    input, and does not pause execution. It becomes a silent programmable node:

        menu = DevMenu(actions, auto=True)
        menu.do("plot")    # runs the action directly

    This makes DevMenu reusable in:
        • visualizers
        • ETL pipelines
        • analytics layers
        • background threads/processes
        • Tkinter-based systems
        • automated testing and scripting

    ----------------------------------------------------------------------
    Modes
    ----------------------------------------------------------------------

    1) Interactive mode (default)
       -----------------------------------------
       menu = DevMenu(actions)
       menu.run()

       - Renders a full CLI menu
       - Hides itself while running actions
       - Displays errors/tracebacks (dev_mode=True)
       - Waits for “Press Enter to return…”
       - Maintains a rolling message log

    2) Auto-mode (non-interactive node)
       -----------------------------------------
       menu = DevMenu(actions, auto=True)
       menu.do("key")

       - Does NOT display the menu
       - Does NOT wait for input
       - Does NOT pause after actions
       - Executes run_action() silently
       - Ideal for programmatic triggers (e.g. visualizer hooks)

    ----------------------------------------------------------------------
    Example
    ----------------------------------------------------------------------

        def greet(name):
            print(f"Hello, {name}!")

        actions = {
            "1": ("Say Hello", greet, ("Alice",), {}),
        }

        # Interactive
        DevMenu(actions, title="Demo").run()

        # Programmatic
        visual = DevMenu(actions, auto=True)
        visual.do("1")      # runs greet("Alice")

    ----------------------------------------------------------------------
    API
    ----------------------------------------------------------------------

    __init__(actions, title="Dev Menu", message_lines=5,
             dev_mode=True, auto=False)
        Initializes the menu object.
        If auto=True, the menu behaves as a silent programmable dispatcher.

    run()
        Starts the interactive loop (ignored in auto-mode).

    do(key)
        Programmatically execute the action associated with `key`.

    run_action(func, args, kwargs)
        Executes the function:
            - clears the screen
            - prints header
            - catches and prints exceptions
            - prints traceback if dev_mode=True
            - in interactive mode only: waits for Enter

    show_menu()
        Renders the menu and the message log (interactive mode only).

    log(msg)
        Adds a message to the rolling log and updates the bottom area.

    ----------------------------------------------------------------------
    Summary
    ----------------------------------------------------------------------
    DevMenu is:
        ✔ a universal CLI menu
        ✔ a silent, scriptable action node (auto-mode)
        ✔ safe to reuse across pipelines, analytics, visualizers
        ✔ independent from UI frameworks (Tkinter/CLI/etc.)
        ✔ ideal for modular, plug-and-play architectures

    """
    def __init__(
        self,
        actions: ActionDict,
        title: str = "Dev Menu",
        message_lines: int = 5,
        dev_mode: bool = True,
        auto: bool = False,
    ):
        self.actions = actions
        self.title = title
        self.message_lines = message_lines
        self.messages: deque[str] = deque(maxlen=message_lines)
        self.dev_mode = dev_mode
        self.auto = auto

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
            if self.dev_mode:
                print(traceback.format_exc())
        if not self.auto:
            input(f"\n{CYAN}Press Enter to return to menu...{RESET}")

    def do(self, key: str):
        """Programmatically execute action by key."""
        action = self.actions.get(key)
        if not action:
            raise KeyError(f"Unknown action '{key}'")

        name, fn, args, kwargs = action
        self.run_action(fnc, args, kwargs)

    def run(self) -> None:
        if self.auto:
            return

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
            if not choice:
                continue

def select_from_list(items: List, title: str = "Select item") -> Any:
    """
    Displays numbered list and returns selected element.
    """
    if not items:
        print(f"\033[1;31mNo items available for selection.\033[0m")
        return None

    print(f"\n\033[1;36m{title}\033[0m\n")
    for i, item in enumerate(items, start=1):
        name = item.name if isinstance(item, Path) else str(item)
        print(f"{i}. {name}")

    while True:
        try:
            choice = input("\n→ Enter number or \"q\" to quit: ")
            if choice.lower() == "q":
                return None
            elif 1 <= int(choice) <= len(items):
                return items[int(choice) - 1]
        except ValueError:
            pass
        print("\033[1;31mInvalid choice, try again.\033[0m")
