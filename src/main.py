import os
import sys
import time
import threading
from dataclasses import dataclass, field
from pick import pick
from game import (
    Difficulty,
    Player,
    Link,
    About,
    RandomWord,
    Highscore,
    DashBoard,
)
from utils import compute_high_score, validate_user_name


@dataclass
class Hangman:
    """
    Hangman class, responbible for managing state throughout the game
    """

    about: About
    player: Player
    wrong_input: bool = field(default=True, init=False)
    begin_counter: bool = field(default=False, init=False)
    pause_counter: bool = field(default=False, init=False)
    time_up: bool = field(default=False, init=False)
    guessed: bool = field(default=False, init=False)
    force_shut: bool = field(default=False, init=False)

    def __post_init__(self):
        self.highscore = Highscore()
        self.dash_board = DashBoard(
            tries=self.player.tries,
            difficulty=self.player.difficulty.value,
            about=self.about,
            high_score=self.highscore,
        )
        self.guessed_letters = []

    def timer(self):
        """
        Timer method
        """
        count = 10000
        while not self.force_shut:
            time.sleep(1)
            count -= 1
            if self.pause_counter:
                count = 1000
            elif self.begin_counter or self.guessed:
                count = 480
            elif count <= 0:
                self.time_up = True
                print("Time is up", flush=True, end=" ")
                break

    def start_timer(self):
        """
        Begin the timer thread
        """
        try:
            timer_thread = threading.Thread(target=self.timer)
            timer_thread.start()
        except KeyboardInterrupt:
            pass
        finally:
            print("timer stopped")

    def clear_screen(self):
        """
        Clear the screen
        """
        os.system("cls" if os.name == "nt" else "clear")
        return True

    @property
    def user_input(self):
        """
        Collect the user guess
        """
        user_input = input("enter an alphabet from A-Z: ").lower()
        if not user_input.isalpha():
            print("Please enter a single character")
            return False
        return user_input

    def exit_confirmation_menu(self):
        """
        User exit game confirmation manue
        """
        self.force_shut = True
        options = ("Yes", "No")
        key, _ = pick(options, indicator="=>", default_index=0, title="Are you sure? ")
        if key.lower() == "yes":
            self.clear_screen()
            sys.exit()

        elif key.lower() == "no":
            self.main_menu()

    def continue_message(self):
        """
        Click any button to continue message
        """

        self.dash_board.console.print(
            "[b red ]Press any key to continue......", justify="center"
        )
        sys.stdin.readline()
        self.main_menu()

    def main_menu(self):
        """
        Game main menu
        """
        self.clear_screen()
        options = ("Play", "Leader board", "About", "Exit")
        key, _ = pick(
            options, indicator="=>", default_index=0, title="Select an option"
        )

        match key.lower():
            case "play":
                self.begin()
            case "leader board":
                self.dash_board.high_score_table()
                self.continue_message()
            case "about":
                self.dash_board.draw_about()
                self.continue_message()
            case "exit":
                self.exit_confirmation_menu()

    def prompt_user_info(self) -> bool:
        """
        User details
        """
        while True:
            self.clear_screen()
            user_name = validate_user_name(value=input("What is your name: "))
            if user_name:
                break
        difficulty = self.select_difficulty()
        self.player.name = user_name
        print(difficulty)
        self.player.difficulty = difficulty
        return True

    def select_difficulty(self) -> Difficulty:
        """
        Select game Difficulty
        """
        self.clear_screen()
        options = (
            Difficulty.EASY.value,
            Difficulty.MEDIUM.value,
            Difficulty.HARD.value,
            "exit",
        )
        key, _ = pick(
            options, indicator="=>", default_index=0, title="Select difficulty"
        )

        match key:
            case Difficulty.EASY.value:
                return Difficulty.EASY
            case Difficulty.MEDIUM.value:
                return Difficulty.MEDIUM
            case Difficulty.HARD.value:
                return Difficulty.HARD
            case "exit":
                self.main_menu()

    def begin(self):
        """
        Begin the game
        """
        self.prompt_user_info()
        while True:
            self.clear_screen()
            difficulty = self.player.difficulty
            random_word = RandomWord(difficulty=difficulty.value)
            guessed_word = "_" * len(random_word.word)
            self.dash_board.hint = random_word.hint
            self.start_timer()
            while self.player.tries <= 8:
                self.wrong_input = True
                self.dash_board.points = self.player.points
                self.dash_board.guessed = guessed_word
                self.clear_screen()
                self.dash_board.draw()
                user_input = self.user_input
                if not user_input:
                    continue
                if self.time_up:
                    break
                for index, _ in enumerate(random_word.word):
                    if random_word.word[index] == user_input:
                        guessed_word_list = list(guessed_word)
                        guessed_word_list[index] = user_input
                        guessed_word = "".join(guessed_word_list)
                        self.dash_board.guessed = guessed_word
                        self.wrong_input = False

                if self.wrong_input:
                    if user_input in self.guessed_letters:
                        self.dash_board.console.print("[b red]You already tried that :)")
                    else:
                        self.dash_board.console.print("[b red]Sorry, try again")
                    self.guessed_letters.append(user_input)
                    self.player.tries += 1
                    self.dash_board.tries = self.player.tries
                    time.sleep(0.5)

                if random_word.word == guessed_word:
                    self.pause_counter = True
                    self.dash_board.console.print(
                        f"correct, the word was [b green]{random_word.word.upper()}"
                    )
                    self.player.points += random_word.points
                    time.sleep(0.5)
                    break

            compute_high_score(player=self.player, high_score=self.highscore)

            if self.player.tries >= 8:
                self.force_shut = True
                sys.stdout.flush()
                self.dash_board.console.print(
                    f"Out of tries. The word was [b red]{random_word.word.upper()}[/b red]\nScore: {self.player.points}"
                )
                time.sleep(0.5)
                break

            if self.time_up:
                self.clear_screen()
                sys.stdout.flush()
                self.dash_board.console.print(
                    f"Out of time. The word was [b red]{random_word.word.upper()}[/b red]\nScore: {self.player.points}"
                )
                time.sleep(3)
                break
        self.main_menu()


if __name__ == "__main__":
    github = Link(
        name="GitHub",
        url="https://github.com/emperorsixpacks/hangman",
    )

    twitter = Link(
        name="Twitter/X",
        url="https://twitter.com/emperorsixpacks",
    )

    about = About(
        name="Hangman",
        links=[github, twitter],
        description="""
            This is a simple hangman game made by emperorsixpacks.

            I really hope you like it. 

            Andrew David
            """,
    )

    player = Player(name=None)
    hangman = Hangman(about=about, player=player)
    
    try:
        hangman.begin()
    except KeyboardInterrupt:
        hangman.main_menu()
