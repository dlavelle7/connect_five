#!/usr/bin/env python3
import sys
import time
import requests

SERVER_URL = "http://127.0.0.1:5000"
CONNECT_URL = f"{SERVER_URL}/connect"
STATE_URL = f"{SERVER_URL}/state"
MOVE_URL = f"{SERVER_URL}/move"
WAIT_INTERVAL = 3


def connect():
    name = input("Enter your name: ")
    response = requests.post(CONNECT_URL, json={"name": name})
    if response.status_code != requests.codes.created:
        print(response.json().get("message"))
        sys.exit()
    return name


def display_board(board):
    for row_idx in range(6):
        row = " ".join(board[col_idx][row_idx] for col_idx in range(9))
        print(row)


def make_move(name):
    # TODO: Validatioin
    column = input(f"It's your turn {name}, please enter column (1 - 9): ")
    data = {
        "column": column,
        "name": name,
    }
    requests.patch(MOVE_URL, json=data)
    # TODO: Was that a valid move (e.g. full -> 400 bad request)


def get_game_state(name):
    response = requests.get(STATE_URL)
    response_data = response.json()
    turn = response_data["turn"]
    if turn == name:
        display_board(response_data["board"])
        make_move(name)
    else:
        if turn is None:
            print("Waiting for another player to join . . .")
        else:
            print(f"Waiting on player {turn} . . .")
        time.sleep(WAIT_INTERVAL)


if __name__ == "__main__":
    # TODO: signals for SIG_TERM => DELETE /connect
    name = connect()
    while True:
        get_game_state(name)
