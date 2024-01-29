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

    def set_syllables(self, syllables: list[str]) -> None:
        """
        Set the syllables in the line, set self.syllables.
        :param syllables: The new syllables.
        :return: None
        """
        self.syllables = syllables

    def set_times(self, times: list[float | int]) -> None:
        """
        Set the starting times of syllables, as well as the end time of the last syllable, set self.times.
        :param times: The new timings.
        :return: None
        """
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
        self.times: list[float | int] = []
        self._start_time = None
        """Start time of the clock"""

    def set_lines(self, lines: list[AbstractLine]) -> None:
        """
        Set self.lines, a list of AbstractLines.
        :param lines: The new AbstractLines.
        :return: None
        """
        self.lines = lines

    def set_times(self, times: list[float | int]) -> None:
        """
        Set self.times, a starting time of all lines.
        :param times: The new timings.
        :return: None
        """
        self.times = times

    def get_construct_lines(self) -> list[str]:
        """
        Get the lines without additional information about syllables or timings.
        :return: The lines in a list.
        """
        result = []
        for line in self.lines:
            result.append(line.construct_line())
        return result

    def start(self) -> None:
        """
        "Start" the "clock". (Actually just set a variable to a value.)
        :return: None
        """
        if self._start_time is None:
            self._start_time = time.perf_counter()
        else:
            self._start_time = time.perf_counter()

    def get_elapsed_time(self, current_time: float | int = None) -> float:
        """
        Get the elapsed time based on the current time.
        :param current_time: The current time to calculate with. If None, time.perf_counter() is used.
        :return: The elapsed time since "starting" the "clock".
        """
        if current_time is None:
            return time.perf_counter() - self._start_time
        else:
            return current_time - self._start_time

    def get_current_lines_syllables_indexes(self, elapsed_time: float | int = None) -> list[list[int, int | None], ...]:
        """
        Get a line and the current syllable in it at the specified or current time.
        Get the index of a line and the currently sung syllable's index in said line at the specified or current time elapsed time.
        If lines overlap, multiple are returned. The order is determined by their order of entry.
        If no syllable is said but a line is already started (like if the line supposedly starts before the singer starts singing), then None is returned in the syllable index's place.
        :param elapsed_time: If None, the elapsed time from the start is used (call self.start()). Otherwise use this as the elapsed time.
        :return: The lines and the currently said syllables in them in the format [[line_index, syllable_index], [line_index, syllable_index]...].
        """
        if elapsed_time is None:
            elapsed_time = time.perf_counter() - self._start_time
        result = []
        for i, line in enumerate(self.lines):
            line_time = self.times[i]
            last_syllable_time = line.times[-1]  # current line's last syllable's end time
            if line_time <= elapsed_time < last_syllable_time + line_time:  # if start of line <= elapsed time < end of last syllable
                result_line_index = i
                result_syllable_index = None
                for j in range(len(line.syllables)):
                    syllable_time = line.times[j]
                    next_syllable_time = line.times[j+1]
                    if syllable_time <= elapsed_time - line_time < next_syllable_time and result_syllable_index is None:  # if syllable start <= elapsed time since start of line < start of next syllable
                        result_syllable_index = j
                result.append([result_line_index, result_syllable_index])
        return result