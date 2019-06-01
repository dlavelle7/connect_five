FROM python:3.6-alpine

RUN mkdir /code
WORKDIR /code

# install dependencies before copying src code, as they won't change as often
COPY requirements.txt requirements_deploy.txt entrypoint*.sh /code/
RUN pip install --upgrade pip && pip install -r requirements_deploy.txt

COPY src /code/src

CMD ["./entrypoint.sh"]
