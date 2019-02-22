#!/usr/bin/env python3
import sys
import time
import requests

SERVER_URL = "http://127.0.0.1:5000"
CONNECT_URL = f"{SERVER_URL}/connect"
STATE_URL = f"{SERVER_URL}/state"
MOVE_URL = f"{SERVER_URL}/move"
WAIT_INTERVAL = 2
ACCEPTED_COLUMNS = [num for num in range(1, 10)]

WIN_RESPONSE = "Win"
OVER = 0


def prompt_user(message):
    return input(message)


def disconnect(message):
    # TODO: Send DELETE /connection request (to reset game state)
    # TODO: Not all disconnections should end the game (e.g. 3rd wheel)
    print(message)
    sys.exit(0)


def connect():
    # TODO: Test
    message = "Enter name: "
    while True:
        name = prompt_user(message)
        response = requests.post(CONNECT_URL, json={"name": name})
        if response.status_code == requests.codes.created:
            return name
        elif response.status_code == requests.codes.forbidden:
            disconnect("This game is already full, try again later.")
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
                # TODO: CLient should determine user message not server
                message = response.json().get("message")
            elif response.status_code == requests.codes.ok:
                message = response.json().get("message")
                if message == WIN_RESPONSE:
                    disconnect("Congrats, you have won!")
                break
            else:
                # TODO: Request error handlin for all requests
                response.raise_for_status()


def get_game_state(name):
    # TODO: raise_for_status()
    response = requests.get(STATE_URL)
    response_data = response.json()
    turn = response_data["turn"]
    game_status = response_data["game_status"]
    if game_status is OVER:
        disconnect(f"Game over, {turn} has won.")
    if turn == name:
        display_board(response_data["board"])
        make_move(name)
    else:
        if turn is None:
            print("Waiting for another player to join . . .")
        else:
            print(f"Waiting on player {turn} . . .")
        time.sleep(WAIT_INTERVAL)


# TODO: signals for SIG_TERM => DELETE /connect
if __name__ == "__main__":
    try:
        name = connect()
        while True:
            # TODO: The client should be a Class instance
            get_game_state(name)
    except requests.ConnectionError:
        disconnect("Could not connect to the game server, is it started?")
    except requests.HTTPError as exc:
        disconnect(f"Game over, request failed with: "
                   f"{exc.response.status_code} {exc.response.reason}.")
