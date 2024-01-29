"""
Internal module that reads and writes a karaoke file in (multiple/one?) file formats and can create an AbstractKaraoke class.
"""

import json

try:
    from ._abstract_karaoke import AbstractKaraoke, AbstractLine
    from ._terminal_printer import screen_print_add_error
except ImportError as e:
    from _abstract_karaoke import AbstractKaraoke, AbstractLine
    from _terminal_printer import screen_print_add_error
    if e.msg == "attempted relative import with no known parent package":
        screen_print_add_error(f"ImportError: {e}; just ignore this")

class _FileFormatParser:

    def get_abstract(self):
        return self.karaoke

class ProprietaryJSON(_FileFormatParser):
    def __init__(self, file: str):
        """
        Proprietary JSON file format for karaoke.
        How it's built up:

{
    "metadata": {  # all metadata is optional, except name and author
        "title": "Song title",
        "author": "Main author (band etc.)",
        "album": "Album name",
        "instruments": "Lead non-singer or band",
        "singer": "Lead singer",
        "features": "featuring XY and WZ etc.",
        "karaoke_lyrics_author": "The author of the lyrics or transcription etc."
        "karaoke_author": "The author of the karaoke like the timing etc.",
        "copyright": "Copyright of the karaoke, NOT the song"
    },
    "karaoke": [
        {
            "syllables": ["En", "ter ", "your ", "ly", "rics ", "here!"],
            "line_start": 10,
            "start_times": [0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.05],
            "end_time": 1.2
        }, etc.
    ]
}

        Support for markdown or HTML depends on the software, not the file format.
        """
        with open(file, "r", encoding="utf-8") as reader:
            raw = reader.read()
        data = json.loads(raw)
        for empty_key in ("title", "author", "album", "instruments", "singer", "features", "karaoke_lyrics"):
            if empty_key not in data["metadata"].keys():
                data["metadata"][empty_key] = None
        self.data = data
        self.metadata = self.data["metadata"]
        self.karaoke = self._parse_karaoke(self.data["karaoke"])

    def _parse_karaoke(self, karaoke) -> AbstractKaraoke:
        abstract_karaoke = AbstractKaraoke()
        abstract_lines = []
        line_starts = []
        for line in karaoke:
            abstract_line = AbstractLine()
            abstract_line.set_syllables(line["syllables"])
            abstract_line.set_times(line["start_times"] + [line["end_time"]])
            abstract_lines.append(abstract_line)
            line_starts.append(line["line_start"])
        abstract_karaoke.set_lines(abstract_lines)
        abstract_karaoke.set_times(line_starts)
        return abstract_karaoke