import json
import os
import random
import sys
import threading
import time
from pick import pick
from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


console = Console()
layout = Layout()


def record_high_score(user, score):
    game_time = time.strftime("%I:%M:%p")
    game_date = time.strftime("%d-%m-%Y")
    with open("scores.txt", "r+") as hs:
        lines = hs.readlines()
        lines.insert(
            1, f"{user},{score},{game_date},{game_time}\n")
        hs.seek(0)
        hs.writelines(lines)
        hs.close()


def compute_high_score(user, score):
    with open("scores.txt", "r") as hs:
        lines = hs.readlines()
        if score > int(lines[1].split(",")[1]):
            record_high_score(user, score)
        hs.close()


def random_word_generator(difficulty, generated_words):
    with open('words.json', 'r') as json_file:
        data = json.load(json_file)
        random_word = random.choice(
            [word for word in data[difficulty] if word["word"] not in generated_words])
        word = random_word["word"]
        meaning = random_word["meaning"]
        points = random_word["points"]
        return word, meaning, points


def game_dashboard(hint, score, display, tries, difficulty):
    hint_panel = Panel(
        hint,
        title="Hint",
    )

    score_panel = Panel(
        str(score),
        title="Score",
        title_align="left",
        width=50
    )
    word_panel = Panel(
        display,
        title="Word",
        title_align="right",
        width=50
    )
    tries_panel = Panel(
        str(tries),
        title="No of tries",
        title_align="right"
    )
    difficulty_panel = Panel(
        difficulty,
        title="Difficulty",
        title_align="left"
    )
    layout.split_column(
        Layout(name="main", size=10),
        hint_panel
    )

    section_1_table = Table.grid(padding=2)
    section_1_table.add_column(no_wrap=True)
    section_1_table.add_row(score_panel)
    section_1_table.add_row(difficulty_panel)

    section_2_table = Table.grid(padding=2)
    section_2_table.add_column(no_wrap=True, justify="right")
    section_2_table.add_row(word_panel)
    section_2_table.add_row(tries_panel)

    layout["main"].split_row(
        Layout(name="section_1"), Layout(name="section_2"))

    layout["section_1"].update(section_1_table)
    layout["section_2"].update(section_2_table)

    console.print(
        Panel(
            layout,
            box=box.DOUBLE,
            padding=(2, 2),
            title="[b yellow] Hangman Game",
            border_style="white"
        ),
        height=20

    )


def timer():
    count = 1000
    while True:
        globals()["begin_counter"] = False
        globals()["pause_counter"] = False
        globals()["guessed"] = False
        globals()["force_shut"] = False
        time.sleep(1)
        count -= 1
        if globals()["pause_counter"]:
            count = 1000
        elif globals()["begin_counter"] or globals()["guessed"]:
            count = 480
        elif count <= 0:
            print("Time is up", flush=True, end=" ")
            break
        elif globals()["force_shut"]:
            break

def get_user_name():
    while True:
        username = input("Enter your username: ").lower()
        if len(username) == 1  or username.isspace() or username.isnumeric():
            print("Please a username")
            continue
        else:
            break
    return username


def main():
    global count
    global guessed
    global begin_counter
    global pause_counter
    global force_shut
    difficulty = "easy"
    score = 0
    generated_words = ["placeholder"]
    user_name = get_user_name()
    timer_thread = threading.Thread(target=timer)
    timer_thread.start()
    while True:
        random_word, hint, points = random_word_generator(
            difficulty, generated_words)
        generated_words.append(random_word.replace("_", " "))
        display = "_"*len(random_word)
        tries = 0
        begin_counter = True

        while timer_thread.is_alive():
            os.system("cls" if os.name == "nt" else "clear")
            game_dashboard(hint, score, display, tries, difficulty)
            if tries >= 8:
                break
            is_wrong = True
            user_input = input("enter an alphabet from A-Z: ").lower()
            if not user_input.isalpha():
                print("Please enter a single character")
                continue
            for letter_index in range(len(random_word)):
                if random_word[letter_index] == user_input:
                    display = list(display)
                    display[letter_index] = user_input
                    is_wrong = False
            if is_wrong:
                print("Sorry, try again", flush=True)
                time.sleep(1)
                tries += 1
                continue
            if random_word.replace(" ", "_").lower() == "".join(display).lower():
                pause_counter = True
                console.print(
                    f'correct, the word was [b green]{"".join(display).replace("_", " ").upper()}')
                time.sleep(3)
                break
            display = "".join(display).upper()
        if tries >= 8:
            globals()["force_shut"] = True
            sys.stdout.flush()
            console.print(
                f'Out of tries. The word was [b red]{random_word.upper()}[/b red]\nScore: {score}')
            time.sleep(3)
            break
        elif not timer_thread.is_alive():
            sys.stdout.flush()
            console.print(
                f'Out of time. The word was [b red]{random_word.upper()}[/b red]\nScore: {score}')
            time.sleep(3)
            break
        score += points
        compute_high_score(user_name, score)
        if len(generated_words) == 5:
            difficulty = "medium"
        if len(generated_words) == 10:
            difficulty = "hard"


def about():

    os.system("cls" if os.name == "nt" else "clear")

    contact_message = Table.grid(padding=1)
    contact_message.add_column(style="red", justify="right")

    contact_message.add_row(
        "Github",
        "[u blue link=https://github.com/emperorsixpacks/hangman]https://github.com/emperorsixpacks/hangman",
    )
    contact_message.add_row(
        "Twitter",
        "[u blue link=https://twitter.com/emperorsixpacks]https://twitter.com/emperorsixpacks",
    )
    intro_message = Text.from_markup(
        """\
This is a simple hangman game made by emperorsixpacks.

I really hope you like it. 

Andrew David
        """
    )
    message = Table.grid(padding=2)
    message.add_column()
    message.add_column(no_wrap=True)
    message.add_row(intro_message, contact_message)

    console.print(
        Panel.fit(
            message,
            box=box.ASCII2,
            padding=(1, 1),
            title="[b yellow] Hangman Game",
            border_style="white"
        ),
        justify="center"
    )
    console.print("[b red ]Press any key to continue......", justify="center")
    sys.stdin.readline()
    main_menu()


def leader_board_table():
    os.system("cls" if os.name == "nt" else "clear")
    table = Table(
        title="Leaderboard")

    table.add_column(
        "Name"
    )

    table.add_column(
        "Score"
    )

    table.add_column(
        "Time"
    )

    table.add_column(
        "Date"
    )

    with open("scores.txt", "r") as sc:
        lines = sc.readlines()

        data = ["".join(user).split(",")
                for user in lines[1:] if user != "\n"]

    for i in range(len(data)):
        table.add_row(
            data[i][0],
            data[i][1],
            data[i][-1],
            data[i][-2],
        )

    table.expand = True
    console.print(table)

    console.print("[b red ]Press any key to continue......", justify="center")
    sys.stdin.readline()
    main_menu()


def main_menu():
    os.system("cls" if os.name == "nt" else "clear")
    options = (
        "Play", "Leader board", "About", "Exit"
    )
    key, index = pick(options, indicator="=>",
                      default_index=0, title="Select an option")

    match key.lower():
        case "play":
            main()
        case "leader board":
            leader_board_table()
        case "about":
            about()
        case "exit":
            exit_confirmation_menu()


def exit_confirmation_menu():
    globals()["force_shut"] = True
    options = ("Yes", "No")
    key, index = pick(options, indicator="=>",
                      default_index=0, title="Are you sure? ")
    if key.lower() == "yes":
        os.system("cls" if os.name == "nt" else "clear")
        sys.exit()

    if key.lower() == "no":
        main_menu()


if __name__ == "__main__":
    try:
        os.system("cls" if os.name == "nt" else "clear")
        main_menu()
    except KeyboardInterrupt:
        os.system("cls" if os.name == "nt" else "clear")
        exit_confirmation_menu()
