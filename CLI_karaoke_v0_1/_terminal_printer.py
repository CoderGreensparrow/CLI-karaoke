"""
Internal module that handles printing to the terminal screen, including "clearing" the screen and positioning things well.
"""

import os, shutil

import colorama

colorama.init()

FALLBACK_TERMINAL_SIZE = (80, 24)
"""Fallback terminal size for shutil.get_terminal_size.
https://docs.python.org/3.10/library/shutil.html#shutil.get_terminal_size"""

_last_terminal_size = None
def get_terminal_size(query_terminal_size: bool = True):
    """
    Get the terminal size or use the fallback value. Or if query_terminal_size is False, use the last known value.
    :param query_terminal_size: Actually get the terminal size or just use the last known one.
    :return: A terminal size.
    """
    global _last_terminal_size
    if query_terminal_size or _last_terminal_size is None:
        terminal_size = shutil.get_terminal_size(FALLBACK_TERMINAL_SIZE)
        _last_terminal_size = [terminal_size.columns, terminal_size.lines]  # don't get an os.terminal_size object
    return _last_terminal_size

errors = []
def screen_print(text: str, scroll: int = 0, input_space: bool = False, query_terminal_size: bool = True, include_errors: bool = True, clear_errors: bool = True):
    """
    Print text starting from the top left part of the screen.
    If the text overflows horizontally, it gets cut off.
    If the text overflows vertically, it gets cut off. But it can be "scrolled" to.
    :param text: The text to print.
    :param scroll: The amount of lines to scroll down. (Or up, negative numbers are allowed)
    :param input_space: Leave one line of space for user input. This function does not take said user input.
    :param query_terminal_size: Get the terminal size before printing. If disabled,
        then the previously known terminal size will be used. May be used to print in a "responsive" way.
    :param include_errors: All saved errors will be printed to the top of all other text, regardless of the main content.
    :param clear_errors: Clear the errors so that they won't be displayed again.
    :return: None
    """
    terminal_size = get_terminal_size(query_terminal_size)
    #  terminal_size[1] -= int(input_space) + 1  # Remove 1 from the screen height regardless
    terminal_size[1] -= 1
    # FORMAT PRINTED TEXT
    if include_errors:
        # 0. ADD ERRORS
        text = "".join(errors) + text
    if clear_errors:
        # CLEAR ERRORS
        errors.clear()
    # 1. HORIZONTAL OVERFLOW CUTOFF
    text_lines = text.splitlines(keepends=True)
    for i, line in enumerate(text_lines):
        if len(line) > terminal_size[0]:
            text_lines[i] = line[0:terminal_size[0]]
    printed = "".join(text_lines)
    # 1. SCROLL
    if scroll < 0:
        printed = os.linesep * -scroll + printed
    elif scroll > 0:
        printed_lines = printed.splitlines(keepends=True)
        printed = "".join(printed_lines[scroll:])
    # 2. PAD LINES
    printed_lines = printed.splitlines(keepends=True)
    if len(printed_lines) < terminal_size[1]:
        printed += os.linesep * (terminal_size[1] - len(printed_lines) + 1)
    elif len(printed_lines) > terminal_size[1]:
        printed = "".join(printed_lines[0:terminal_size[1]])
    # PRINT TEXT
    print(printed, end="")

def screen_print_add_error(full_error: str):
    errors.append(colorama.Fore.RED + f"ERROR: {full_error}" + colorama.Fore.RESET + os.linesep)


def choice_input(choices: list[str], prompt: str = None, invalid_choice_text: str = None):
    """
    Get predefined user input. Asks the user until it gets a question.
    :param choices: The choices the user can make.
    :param prompt: The text to display before the user input. Default is the choices separated by " / " and ": ".
    :param invalid_choice_text: The text to print if an invalid choice is entered. Default is the inputted invalid choice and a question mark (?).
        The invalid_choice_text is formatted, so you can include a {} to get the invalid choice.
    :return: The selected choice.
    """
    if prompt is None:
        prompt = " / ".join(choices) + ": "
    if invalid_choice_text is None:
        invalid_choice_text = "{}?"
    choice = None
    while choice not in choices:
        choice = input(prompt)
        if choice not in choices:
            print(invalid_choice_text.format(choice))
            choice = None
    return choice

def path_input(prompt: str = "Path: ", invalid_path_text: str = None) -> str:
    """
    Get a valid path input from the user. Checked with os.path.exists.
    :param prompt: The text to display before the user input. Default is "Path: ".
    :param invalid_path_text: The text to print if an invalid path is entered. Default is the inputted invalid path and a question mark (?).
        The invalid_path_text is formatted, so you can include a {} to get the invalid path.
    :return: The path.
    """
    if invalid_path_text is None:
        invalid_path_text = "{}?"
    path = None
    while path is None or not os.path.exists(path):
        path = input(prompt)
        if not os.path.exists(path):
            print(invalid_path_text.format(path))
            path = None
    return path