"""
GUIless, in CLI karaoke package in Python.
Potential extra functionality: Create karaoke animation with Manim
(Yes, Manim. I know it was probably not designed for that, but it can look nice.
And why should I not use code I've already written to parse karaoke files and such?
Think of it like an extra.)

Dependencies (see requirements.txt):
colorama
"""

import colorama

colorama.init()

try:
    from ._terminal_printer import screen_print, choice_input
    from .player import main as player_main
    from .writer import main as writer_main
except ImportError as e:
    from _terminal_printer import screen_print, screen_print_add_error, choice_input
    from player import main as player_main
    from writer import main as writer_main
    if e.msg == "attempted relative import with no known parent package":
        screen_print_add_error(f"ImportError: {e}; just ignore this")

def hub():
    screen_print(
"""
    Welcome to CLI karaoke!
    Please choose from the following options: 

        A Open player (play karaoke files without music)
        B Open writer (create or edit karaoke files)
        C Exit""",
        input_space=True
    )
    choice = choice_input(["A", "B", "C"], "\tEnter a letter, A, B or C: ", "There is no choice {}. Please enter another letter.")
    if choice == "A":
        player_main()
    elif choice == "B":
        writer_main()
    elif choice == "C":
        screen_print("\n\tGoodbye!", input_space=True)
        exit()

if __name__ == '__main__':
    hub()