# Connect 5 [![Build Status](https://travis-ci.com/dlavelle7/connect_five.svg?branch=master)](https://travis-ci.com/dlavelle7/connect_five)

## Dependencies
* Python 3.6
* pip

## Installation
```
git clone git@github.com:dlavelle7/connect_five.git
cd connect_five

# preferably in a python virtual env
pip install -r requirements.txt
```

## Usage
Run the server:
```
FLASK_APP=src.server.app.py flask run
```

In a separate shell, run the first client:
```
python src/client.py
```

In a separate shell, run the second client:
```
python src/client.py
```

## Approach

The board is a list of lists. Each "column" in the board is a list. The far
left column on the users screen is the first position in the board list.

The bottom of a "column" corresponds to the last position in that list.

## Simplifications

For the purpose of this exercise I have chosen to run the server application
using Flask's development server. In a production setting this would need to be
replaced by a WSGI HTTP server like `gunicorn` or `uwsgi`.

The development server has threaded mode enabled by default, meaning each
request will be handled in a separate thread.

In the event of a draw game, players will disconnect themselves.

A subsequent new game requires the server to be restarted.

Clients are considered "connected" after they has entered an appropriate name.

## Testing

Pytest was chosen as the test runner. The unit tests themselves are written
using the `unittest` framework.

Run the unit tests:
```
pip install -r requirement_test.txt

pytest tests/
```

Tox was chosen as the CI automation too and runs the following tests:
* unit tests
* unit test coverage (greater than 70%)
* static code analysis `flake8`

Run the CI build locally:
```
pip install -r requirements_ci.txt

tox
```

Travis CI is used as to automate the CI build (tox) whenever change is
detected to a branch on GitHub (click the "build" image on this readme for
build info).
