# Connect 5 [![Build Status](https://travis-ci.com/dlavelle7/connect_five.svg?branch=master)](https://travis-ci.com/dlavelle7/connect_five)

## What's New
[v3.0 TBC]
* Dockerized server
* Replaced in memory game state with Redis container
* Replaced Flask dev server with WSGI server (gunicorn)
* docker-compose used to bring up server & redis containers
* "debug mode" docker-compose file for breakpoints & src code mounting
* [TODO] better unit testing
** less mocking
** more descriptive test method names

[v2.0]
* Game server now supports multiple concurrent games (no more restarting)
* More RESTful URIs ("game" resource being manipulated and accessed via /game)
* Code refactor:

  * Refactored similar "check" functions
  * Removed hardcoded board dimensions and winning count number

## Dependencies
* Python 3.6
* pip
* Docker

## Installation
```
git clone git@github.com:dlavelle7/connect_five.git
cd connect_five

# preferably in a python virtual env
pip install -r requirements_run.txt
```

## Usage
Run the server:
```
docker-compose up --build
```

In a separate shell, run the first client:
```
python src/client.py
```

In a separate shell, run the second client:
```
python src/client.py
```

### Debugging
Run the server in "debug" mode:
```
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

## Approach

The server is written using the Flask framework and the clients communicate
with the server over HTTP using the `requests` library.

The board is a list of lists. Each "column" in the board is an individual list.
The far left column on the user's screen is the first position in the board
list.

The bottom of a "column" corresponds to the last position in that list.

## Simplifications

In the event of a draw game, players will disconnect themselves.

## Assumptions

Clients are considered "connected" after they has entered an appropriate name.

The first player to connect will go first and be assigned "Xs".

## Testing

Pytest was chosen as the test runner. The unit tests themselves are written
using the `unittest` framework.

Run the unit tests:
```
pip install -r requirements_test.txt

pytest tests/
```

Tox was chosen as the CI automation tool and runs the following tests:
* unit tests
* unit test coverage (greater than 75%)
* static code analysis `flake8`

Run the CI build locally:
```
pip install -r requirements_ci.txt

tox
```

Travis CI is used to automate the CI build (tox), whenever a change is
detected to a branch on GitHub (click the "build" image on this readme for
build info).
