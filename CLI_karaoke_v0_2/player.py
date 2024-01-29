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
        self.all_lines = self.karaoke.get_construct_lines()
        self.all_syllables = [self.karaoke.lines[line_index].syllables for line_index in range(len(self.karaoke.lines))]
        self.color_line_not_playing = colorama.Style.DIM + colorama.Fore.WHITE
        self.color_syllable_played = colorama.Style.DIM + colorama.Fore.YELLOW
        self.color_syllable_playing = colorama.Style.BRIGHT + colorama.Fore.LIGHTYELLOW_EX
        self.color_syllable_will_play = colorama.Style.DIM + colorama.Fore.YELLOW
        self.color_reset = colorama.Style.RESET_ALL
        self._scroll = 0  # The amount of scrolling. Increases in increments of 10.
        self._SCROLL_INCREMENT = 10

    def render_frame(self):
        terminal_size = get_terminal_size(False)
        # I. Get data
        # 1. Get the line, syllable data
        data = self.karaoke.get_current_lines_syllables_indexes()
        # II. Parse the data
        line_indexes = []
        syllable_indexes = []
        # 2. Separate line and syllable indexes
        for line_index, syllable_index in data:
            line_indexes.append(line_index)
            syllable_indexes.append(syllable_index)
        # III. Form the output
        # 3. Scroll if required
        if len(line_indexes) != 0:
            if max(line_indexes) + 4 - self._scroll > terminal_size[1] - 4:
                self._scroll += self._SCROLL_INCREMENT
        # 4. Title
        text = "\n\t\t" + self.metadata["title"] + "\n\n"
        # 5. Lines
        """for line_pointer in range(0 + self._scroll, min(len(self.all_lines), terminal_size[1] - 8)):
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
        text += self.color_reset"""
        for line_index in range(0 + self._scroll, min(len(self.all_lines), terminal_size[1] - 8)):
            if line_index in line_indexes:  # This line is being played
                for i, syllable in enumerate(self.all_syllables[line_index]):
                    #  text += f"{line_index}; {i} - {syllable}"
                    current_syllable = syllable_indexes[line_indexes.index(line_index)]
                    if current_syllable is None:
                        text += self.color_syllable_will_play
                    elif i == current_syllable:  # If we're currently printing the played syllable
                        text += self.color_syllable_playing
                    elif i < current_syllable:  # We already played this syllable
                        text += self.color_syllable_played
                    elif i > current_syllable:  # Will play this syllable
                        text += self.color_syllable_will_play
                    text += syllable
            else:
                text += self.color_line_not_playing + self.all_lines[line_index]
            text += "\n"
        text += self.color_reset
        text += "\ndata variable: " + str(data)
        text += "\n" + str(line_indexes) + ", " + str(syllable_indexes) + " --- " + str([self.all_lines[line_index] for line_index in line_indexes])
        screen_print_add_error("This code is currently not working. Please fix it up. The things in section II. may be wrong. See the issue by running with test copy.json.")
        # IV. print
        screen_print(text, include_errors=False, clear_errors=False)

    def start(self, refresh_rate: float = 1/120):
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