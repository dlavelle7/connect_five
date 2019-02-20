#!/usr/bin/env python3
import requests

SERVER_URL = "http://127.0.0.1:5000"
CONNECT_URL = f"{SERVER_URL}/connect"


def play():
    name = input("Enter your name: ")
    response = requests.post(CONNECT_URL, json={"name": name})
    print(response.json())


if __name__ == "__main__":
    # TODO: try/finally for SIG_TERM => DELETE /connect
    #while True:
    play()
