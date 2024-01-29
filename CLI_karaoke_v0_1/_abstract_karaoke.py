"""
Internal module that contains a universal representation of a karaoke for the program to work with.
It also contains functions for handling the playing of said karaoke by getting the right syllables and lines at the right time.
"""

import time

class AbstractLine:
    def __init__(self):
        """
        A universal representation of a line of karaoke.
        It also contains functions for handling the playing of said karaoke by getting the right syllables and lines at the right time.
        :var self.syllables: The syllables in the line.
        :var self.times: The starting time of said syllable inside the line relative to the start of the line. The last item is the end of the last syllable.
        """
        self.syllables: list[str] = []
        self.times: list[float | int] = []

    def set_syllables(self, syllables):
        self.syllables = syllables

    def set_times(self, times):
        self.times = times

    def construct_line(self) -> str:
        """
        Get the line itself without any syllable or time markers.
        :return: The line itself.
        """
        return "".join(self.syllables)

class AbstractKaraoke:
    def __init__(self):
        """
        A universal representation of a karaoke.
        :var self.lines: The lines in a karaoke.
        :var self.times: The staring times of said lines inside the karaoke relative to the start of the karaoke.
        """
        self.lines: list[AbstractLine] = []
        self.times: list[int | float] = []
        self._start_time = None
        """Start time of the clock"""

    def set_lines(self, lines):
        self.lines = lines

    def set_times(self, times):
        self.times = times

    def start(self):
        """
        "Start" the "clock". (Actually just set a variable to a value.)
        :return: None
        """
        if self._start_time is None:
            self._start_time = time.perf_counter()
        else:
            self._start_time = time.perf_counter()

    def get_elapsed_time(self, current_time: float | int = None):
        """
        Get the elapsed time based on the current time.
        :param current_time: The current time to calculate with. If None, time.perf_counter() is used.
        :return: The elapsed time since "starting" the "clock".
        """
        if current_time is None:
            return time.perf_counter() - self._start_time
        else:
            return current_time - self._start_time

    def query_lines_syllables(self, elapsed_time: float | int = None) -> list[list[str, str], ...]:
        """
        Get a line and the current syllable in it at the specified or current time.
        If lines overlap, multiple are returned. The order is determined by their order of entry.
        If no syllable is said but a line is already started (like if the line supposedly starts before the singer starts singing), then None is returned in the syllable's place.
        :param elapsed_time: If None, the elapsed time from the start is used (call self.start()). Otherwise use this as the elapsed time.
        :return: The lines and the currently said syllables in them in the format [[line, syllable], [line, syllable]...].
        """
        if elapsed_time is None:
            elapsed_time = time.perf_counter() - self._start_time
        result = []
        for i, line in enumerate(self.lines):
            if self.times[i] <= elapsed_time < line.times[-1] + self.times[i]:  # if start of line <= elapsed time < end of last syllable
                result_line = line.construct_line()
                result_syllable = None
                for j in range(len(line.times) - 2):
                    syllable_time = line.times[j]
                    if syllable_time <= elapsed_time - self.times[i] < line.times[j+1]:  # if syllable start <= elapsed time since start of line < start of next syllable
                        result_syllable = line.syllables[j]
                result.append([result_line, result_syllable])
        return result