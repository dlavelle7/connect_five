#!/usr/bin/env python3
"""Client module for communicating with server and displaying game state."""
import sys
import time
import signal
import requests

SERVER_URL = "http://127.0.0.1"
GAME_URL = f"{SERVER_URL}/game"

WAIT_INTERVAL = 2
ACCEPTED_COLUMNS = [num for num in range(1, 10)]
JOIN_GAME = "1"
NEW_2P_GAME = "2"
NEW_3P_GAME = "3"
ACCEPTED_GAME_TYPES = (JOIN_GAME, NEW_2P_GAME, NEW_3P_GAME)

GAME_WON = "won"
GAME_DISCONNECTED = "disconnected"
BOARD_ROWS = 6
BOARD_COLS = 9


def prompt_user(message):
    return input(message)


def exit_game(message):
    print(message)
    sys.exit(0)


def connect():
    """Get player name, choose game type and connect player to game."""
    message = "Enter name: "
    name = prompt_user(message)
    message = (
        "1. Join existing game\n"
        "2. Create new two player game\n"
        "3. Create new three player game\n"
        "Select game type: "
    )

    while True:
        game_type = prompt_user(message)
        if game_type in ACCEPTED_GAME_TYPES:
            break
        message = "Invalid choice, please select 1, 2 or 3: "

    if game_type == JOIN_GAME:
        while True:
            response = requests.patch(GAME_URL, json={"name": name})
            if response.status_code == requests.codes.ok:
                game_id = response.json()["game_id"]
                return name, game_id
            elif response.status_code == requests.codes.not_found:
                print("Waiting for an available space . . . ")
                time.sleep(WAIT_INTERVAL)
            else:
                response.raise_for_status()
    else:
        max_players = int(game_type)
        body = {
            "name": name,
            "max_players": max_players,
        }
        response = requests.post(GAME_URL, json=body)
        if response.status_code == requests.codes.created:
            game_id = response.json()["game_id"]
            return name, game_id
        else:
            response.raise_for_status()


def display_board(board):
    """Display the state of the board to the user."""
    for row_idx in range(BOARD_ROWS):
        row = " ".join(board[col_idx][row_idx]
                       for col_idx in range(BOARD_COLS))
        print(row)


class Client:
    """Class representing a connected player in game."""

    def __init__(self, player_name, game_id):
        self.name = player_name
        self.game_id = game_id

    @property
    def client_game_url(self):
        return f"{GAME_URL}/{self.game_id}"

    def play(self):
        try:
            self.get_game_state()
        except requests.HTTPError as exc:
            print(f"{exc.response.status_code} {exc.response.reason}.")  # log
            self.disconnect("Game over, could not process request.")

    def get_game_state(self):
        """Poll server for current game state."""
        response = requests.get(self.client_game_url)
        response.raise_for_status()
        response_data = response.json()
        turn = response_data["turn"]
        game_status = response_data["game_status"]
        if game_status == GAME_WON:
            board = response.json().get("board")
            display_board(board)
            exit_game(f"Game over, {turn} has won.")
        elif game_status == GAME_DISCONNECTED:
            exit_game(f"Game over, other player disconnected.")
        elif turn == self.name:
            display_board(response_data["board"])
            self.make_move()
        else:
            if turn is None:
                print("Waiting for another player to join . . .")
            else:
                print(f"Waiting on player {turn} . . .")
            time.sleep(WAIT_INTERVAL)

    def make_move(self):
        """Get valid move from player and communicate move to server."""
        message = f"It's your turn {self.name}, please enter column (1 - 9): "
        while True:
            column = prompt_user(message)
            try:
                column = int(column)
                assert column in ACCEPTED_COLUMNS
            except (AssertionError, ValueError):
                message = "Invalid choice, please enter column (1 - 9): "
            else:
                data = {
                    "column": column,
                    "name": self.name,
                }
                response = requests.patch(self.client_game_url, json=data)
                if response.status_code == requests.codes.bad_request:
                    message = f"Column {column} is full, please try another: "
                elif response.status_code == requests.codes.ok:
                    board = response.json().get("board")
                    display_board(board)
                    message = response.json().get("message")
                    if message == GAME_WON:
                        exit_game("Congrats, you have won!")
                    break
                else:
                    response.raise_for_status()

    def signal_handler(self, sig_num, frame):
        self.disconnect("Game over, you disconnected.")

    def register_signal_handlers(self):
        """Register hanlders for client disconnections such as:

        - Hang up signal
        - Interrupt signal
        - Termination signal
        """
        for sig_num in {signal.SIGTERM, signal.SIGINT, signal.SIGHUP}:
            signal.signal(sig_num, self.signal_handler)

    def disconnect(self, message):
        """Connected client leaves the game, inform server to end game."""
        disconnected_body = {"game_status": GAME_DISCONNECTED}
        requests.patch(self.client_game_url, json=disconnected_body)
        exit_game(message)


if __name__ == "__main__":
    try:
        name, game_id = connect()
        client = Client(name, game_id)
        client.register_signal_handlers()
        while True:
            client.play()
    except requests.ConnectionError as exc:
        print(exc)  # log
        exit_game("Could not connect to the game server, is it running?")
