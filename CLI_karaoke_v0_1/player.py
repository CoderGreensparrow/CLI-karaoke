"""
Karaoke player for (multiple?) karaoke file types.
"""

import time

import colorama

try:
    from ._terminal_printer import screen_print, screen_print_add_error, choice_input, path_input, get_terminal_size
    from ._abstract_karaoke import AbstractKaraoke, AbstractLine
    from ._file_IO import ProprietaryJSON
except ImportError as e:
    from _terminal_printer import screen_print, screen_print_add_error, choice_input, path_input, get_terminal_size
    from _abstract_karaoke import AbstractKaraoke, AbstractLine
    from _file_IO import ProprietaryJSON
    if e.msg == "attempted relative import with no known parent package":
        screen_print_add_error(f"ImportError: {e}; just ignore this")

class Player:
    def __init__(self, metadata: dict, karaoke: AbstractKaraoke):
        """
        A player object.
        :param metadata: The metadata
        :param karaoke: AbstractKaraoke
        """
        self.metadata = metadata
        self.karaoke = karaoke
        self.all_lines = [line.construct_line() for line in self.karaoke.lines]
        self.all_syllables = [self.karaoke.lines[line_index].syllables for line_index in range(len(self.karaoke.lines))]
        self.color_line_not_playing = colorama.Style.DIM + colorama.Fore.WHITE
        self.color_syllable_played = colorama.Style.DIM + colorama.Fore.YELLOW
        self.color_syllable_playing = colorama.Style.BRIGHT + colorama.Fore.LIGHTYELLOW_EX
        self.color_syllable_will_play = colorama.Style.DIM + colorama.Fore.YELLOW
        self.color_reset = colorama.Style.RESET_ALL
        self._scroll = 0  # The amount of scrolling. Increases in increments of 10.
        self._SCROLL_INCREMENT = 10
        self._line_pointers: list[int] = []
        self._syllable_pointers: list[int] = []

    def render_frame(self):
        terminal_size = get_terminal_size(False)
        # Because of the way I implemented all of this, this is going to get messy...
        # I. Get data
        # 1. Get the line, syllable data
        data = self.karaoke.query_lines_syllables()
        # II. Understand the data
        # 2. Collect the current lines in use
        _current_line_pointers = []
        for line, syllable in data:
            line_pointer = self.all_lines.index(line)
            _current_line_pointers.append(line_pointer)
            # 2B. And also scroll if needed
            if line_pointer + 1 > terminal_size[1] - 8:
                self._scroll += self._SCROLL_INCREMENT
        # 3. Compare to the last known lines.
        # 3A. If one of the lines in the new one isn't present, delete from the old pointers, as well as the syllable pointers.
        for i, last_pointer in enumerate(self._line_pointers):
            if last_pointer not in _current_line_pointers:
                self._line_pointers.pop(i)
                self._syllable_pointers.pop(i)
        # 3B. If one of the lines in the old one isn't present compared to the new ones, add the new one as well as create new syllable pointers.
        for i, current_pointer in enumerate(_current_line_pointers):
            if current_pointer not in self._line_pointers:
                self._line_pointers.append(current_pointer)
                self._syllable_pointers.append(0)  # The starting syllable pointer, starting from the first syllable in the list
        # 4. Now for the syllables. Search in the syllables starting from the syllable pointer until a match is found.
        # a) Go through each line
        for line_pointer in self._line_pointers:
            syllables = self.karaoke.lines[line_pointer].syllables  # I could use self.syllables[line_index] in theory
            found = False
            for syllable_index in range(self._syllable_pointers[line_pointer], len(syllables)):
                # b) Search only the required line
                for line, syllable in data:
                    if line == self.all_lines[line_pointer]:
                        # c) If the syllable we're searching for matches the currently looked at syllable
                        if syllables[syllable_index] == syllable:
                            found = True
                if found:
                    break
        # III. Form the output
        text = "\n\t\t" + self.metadata["title"] + "\n\n"
        for line_pointer in range(0 + self._scroll, min(len(self.all_lines), terminal_size[1] - 8)):
            if line_pointer in self._line_pointers:  # This line is being played
                for i, syllable in enumerate(self.all_syllables[line_pointer]):
                    if i == self._syllable_pointers[line_pointer]:  # If we're currently printing the played syllable
                        text += self.color_syllable_playing
                    elif i < self._syllable_pointers[line_pointer]:  # We already played this syllable
                        text += self.color_syllable_played
                    elif i > self._syllable_pointers[line_pointer]:  # Will play this syllable
                        text += self.color_syllable_will_play
                    text += syllable
            if line_pointer not in self._line_pointers:  # This line is not being played
                text += self.color_line_not_playing + self.all_lines[line_pointer]
            text += "\n"
        text += self.color_reset
        text += "\ndata variable: " + str(data)
        text += "\n" + str(self._line_pointers) + ", " + str(self._syllable_pointers)
        screen_print_add_error("This code is currently not working. Please fix it up. The things in section II. may be wrong. See the issue by running with test copy.json.")
        # IV. print
        screen_print(text, include_errors=True, clear_errors=True)

    def start(self, refresh_rate: float = 1/10):
        """
        Start displaying a karaoke.
        :param refresh_rate: The refresh rate of the screen.
        :return: None
        """
        end_time = self.karaoke.lines[-1].times[-1]
        self.karaoke.start()
        while self.karaoke.get_elapsed_time() <= end_time:  # while in time
            self.render_frame()
            time.sleep(refresh_rate)

def main():
    screen_print(
"""
    Welcome to the CLI karaoke player!
    
    Please enter the name of the file you want to play.
    Use one of the following file formats:
        - .json (a proprietary way of using JSON to store karaoke information, see the _file_IO.py module)
    
    Please note that this program doesn't play music, you need to sync that yourself.
    Before the karaoke starts, it will have a 5 second countdown so you can sync the music with the karaoke text.""",
        input_space=True
    )
    path = path_input("\tPath: ", "{} is an invalid/nonexistent path. Please enter the path to the karaoke file.")
    if path.endswith(".json"):
        parser = ProprietaryJSON(path)
        karaoke = parser.karaoke
        metadata = parser.metadata
    player = Player(metadata, karaoke)
    player.start()

if __name__ == "__main__":
    main()