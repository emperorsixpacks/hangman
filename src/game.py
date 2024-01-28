""" 
    This file contains game information and classess
"""

from dataclasses import dataclass, field
from enum import Enum
import time
import random
from typing import List
import json
from rich import layout, panel, table, console, box, text


class Difficulty(Enum):
    """
    Game difficulty
    """

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class Player:
    """
    Player information
    """

    name: str
    difficulty: Difficulty = field(default=Difficulty.EASY)
    tries: int = field(default=0, init=False)
    points: int = field(default=0, init=False)
    time: str = field(default_factory=lambda: time.strftime("%d-%m-%Y"), init=False)
    date: str = field(default_factory=lambda: time.strftime("%I:%M:%p"), init=False)


@dataclass
class Link:
    """
    Author's contact details
    """

    name: str
    url: str


@dataclass
class About:
    """
    About info
    """

    name: str
    description: str
    links: List[Link]


@dataclass
class Word:
    """
    A representation of a word
    """

    word: str
    hint: str
    points: int

    def __str__(self) -> str:
        return self.word


@dataclass
class RandomWord:
    """
    A random word object
    """

    difficulty: Difficulty
    word: str = field(init=False)
    hint: str = field(init=False)
    points: int = field(init=False)

    _generated_words: List[str] = field(
        default_factory=lambda: ["placeholder"], init=False
    )

    def __post_init__(self) -> None:
        if len(self._generated_words) == 33:
            return True
        file = self.__open()
        words = json.load(next(file))
        random_word = random.choice(
            [
                word
                for word in words[self.difficulty]
                if word["word"] not in self._generated_words
            ]
        )
        self.word = random_word["word"]
        self.hint = random_word["meaning"]
        self.points = random_word["points"]

    def append(self, word_to_append: Word) -> True:
        """
        Append a new word to the list of generated random words
        """
        self._generated_words.append(word_to_append.word)
        return True

    def __open(self):
        with open("words.json", "r", encoding="utf-8") as file:
            yield file


@dataclass
class Highscore:
    """
    Highscore class
    """

    curent_high_score: int | None = field(default=None)
    current_holder: str | None = field(default=None)

    def __post_init__(self):
        self.__file = self.open_file()
        self.scores = next(self.__file).readlines()
        self.curent_high_score = int(self.scores[1].split(",")[1])
        self.current_holder = self.scores[1].split(",")[0]
        self.__file.close()

    def insert(self, player: Player):
        """
        add a new high points
        """
        self.scores.insert(
            1,
            f"{player.player.name},{player.player.points},{player.date},{player.time}\n",
        )
        self.__file.close()

    @classmethod
    def open_file(cls):
        """
        open the score.txt file
        """
        with open("scores.txt", "r+", encoding="utf-8") as file:
            yield file


@dataclass
class DashBoard:
    """
    Dashboard component
    """

    tries: str
    about: About
    difficulty: Difficulty
    high_score: Highscore
    points: str = field(default="None", init=False)
    hint: str = field(default="None", init=False)
    guessed: str = field(default="None", init=False)

    def __post_init__(self):
        self.console = console.Console()
        self.layout = layout.Layout()

    def draw(self):
        """
        Draw dashboard
        """
        hint_panel = panel.Panel(
            self.hint,
            title="Hint",
        )

        score_panel = panel.Panel(
            str(self.points), title="points", title_align="left", width=50
        )
        word_panel = panel.Panel(
            self.guessed, title="Word", title_align="right", width=50
        )
        tries_panel = panel.Panel(
            str(self.tries), title="No of tries", title_align="right"
        )
        difficulty_panel = panel.Panel(
            self.difficulty, title="Difficulty", title_align="left"
        )
        self.layout.split_column(layout.Layout(name="main", size=10), hint_panel)

        section_1_table = table.Table.grid(padding=2)
        section_1_table.add_column(no_wrap=True)
        section_1_table.add_row(score_panel)
        section_1_table.add_row(difficulty_panel)

        section_2_table = table.Table.grid(padding=2)
        section_2_table.add_column(no_wrap=True, justify="right")
        section_2_table.add_row(word_panel)
        section_2_table.add_row(tries_panel)

        self.layout["main"].split_row(
            layout.Layout(name="section_1"), layout.Layout(name="section_2")
        )

        self.layout["section_1"].update(section_1_table)
        self.layout["section_2"].update(section_2_table)

        self.console.print(
            panel.Panel(
                self.layout,
                box=box.DOUBLE,
                padding=(2, 2),
                title=f"[b yellow] {self.about.name}",
                border_style="white",
            ),
            height=20,
        )

    def draw_about(self):
        """
        Draw about game section
        """

        contact_message = table.Table.grid(padding=1)
        contact_message.add_column(style="red", justify="right")

        for link in self.about.links:
            contact_message.add_row(link.name, f"[u blue link={link.url}]{link.name}")

        intro_message = text.Text.from_markup(self.about.description)
        message = table.Table.grid(padding=2)
        message.add_column(no_wrap=True)
        message.add_row(intro_message, contact_message)

        self.console.print(
            panel.Panel.fit(
                message,
                box=box.ASCII2,
                padding=(2, 1),
                title=f"[b yellow] {self.about.name}",
                border_style="white",
            ),
            justify="center",
        )

    def high_score_table(self):
        """
        Draw highscore table
        """
        high_score_table = table.Table(title="Leaderboard")

        high_score_table.add_column("Name")

        high_score_table.add_column("points")

        high_score_table.add_column("Time")

        high_score_table.add_column("Date")

        file = self.high_score.open_file()

        lines = next(file).readlines()

        scores = ["".join(user).split(",") for user in lines[1:] if user != "\n"]

        for i, _ in enumerate(scores):
            high_score_table.add_row(
                scores[i][0],
                scores[i][1],
                scores[i][-1],
                scores[i][-2],
            )

        high_score_table.expand = True
        self.console.print(high_score_table)
