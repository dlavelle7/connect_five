#!/usr/bin/env python3
import sys
import time
import signal
import requests

SERVER_URL = "http://127.0.0.1:5000"
CONNECT_URL = f"{SERVER_URL}/connect"
STATE_URL = f"{SERVER_URL}/state"
MOVE_URL = f"{SERVER_URL}/move"
WAIT_INTERVAL = 2
ACCEPTED_COLUMNS = [num for num in range(1, 10)]

WIN_RESPONSE = "won"
DISCONNECTED_RESPONSE = "disconnected"


def prompt_user(message):
    return input(message)


def exit_game(message):
    print(message)
    sys.exit(0)


def disconnect(message, name):
    """Connect client leaves the game, inform server."""
    requests.delete(CONNECT_URL, json={"name": name})
    exit_game(message)


def connect():
    message = "Enter name: "
    while True:
        name = prompt_user(message)
        response = requests.post(CONNECT_URL, json={"name": name})
        if response.status_code == requests.codes.created:
            return name
        elif response.status_code == requests.codes.forbidden:
            exit_game("This game is already full, try again later.")
        elif response.status_code == requests.codes.conflict:
            message = (
                "That name is already taken, please enter a different name: ")
        else:
            response.raise_for_status()


def display_board(board):
    for row_idx in range(6):
        row = " ".join(board[col_idx][row_idx] for col_idx in range(9))
        print(row)


def make_move(name):
    message = f"It's your turn {name}, please enter column (1 - 9): "
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
                "name": name,
            }
            response = requests.patch(MOVE_URL, json=data)
            if response.status_code == requests.codes.bad_request:
                message = f"Column {column} is full, please try another: "
            elif response.status_code == requests.codes.ok:
                board = response.json().get("board")
                display_board(board)
                message = response.json().get("message")
                if message == WIN_RESPONSE:
                    exit_game("Congrats, you have won!")
                break
            else:
                response.raise_for_status()


def get_game_state(name):
    # TODO: raise_for_status()
    response = requests.get(STATE_URL)
    response_data = response.json()
    turn = response_data["turn"]
    game_status = response_data["game_status"]
    if game_status == WIN_RESPONSE:
        board = response.json().get("board")
        display_board(board)
        exit_game(f"Game over, {turn} has won.")
    elif game_status == DISCONNECTED_RESPONSE:
        exit_game(f"Game over, other player disconnected.")
    elif turn == name:
        display_board(response_data["board"])
        make_move(name)
    else:
        if turn is None:
            print("Waiting for another player to join . . .")
        else:
            print(f"Waiting on player {turn} . . .")
        time.sleep(WAIT_INTERVAL)


def sigterm_handler(sig_num, frame):
    disconnect("Game over, you disconnected.", name)


# TODO: maybe only do it when you have connected to server
def register_signal_handlers():
    """Register hanlders for client disconnections such as:

    - Hang up signal
    - Interrupt signal
    - Termination signal
    """
    for sig_num in {signal.SIGTERM, signal.SIGINT, signal.SIGHUP}:
        signal.signal(sig_num, sigterm_handler)


if __name__ == "__main__":
    try:
        name = connect()
        register_signal_handlers()
        while True:
            # TODO: The client should be a Class instance
            get_game_state(name)
    except requests.ConnectionError:
        exit_game("Could not connect to the game server, is it started?")
    except requests.HTTPError as exc:
        disconnect(f"Game over, request failed with: "
                   f"{exc.response.status_code} {exc.response.reason}.",
                   name)
