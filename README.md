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

## Assumptions / Simplifications

For the purpose of this exercise I have chosen to run the server application
using Flask's development server. In a production setting this would need to be
replaced by a WSGI HTTP server like `gunicorn` or `uwsgi`.

The development server has threaded mode enabled by default, meaning each
request will be handled in a separate thread.
