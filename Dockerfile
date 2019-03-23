FROM python:3.6-alpine

RUN mkdir /code
WORKDIR /code

# install dependencies before copying src code, as they won't change as often
COPY requirements.txt /code
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY src /code/src
