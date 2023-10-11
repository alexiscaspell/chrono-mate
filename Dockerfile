FROM python:3.8-slim

WORKDIR /usr/src/

ENV TZ="America/Argentina/Buenos_Aires"

COPY ./requirements.txt .

RUN pip install -r requirements.txt

RUN rm requirements.txt

# COMPILACION
COPY ./app.py ./
COPY ./model ./model
COPY ./utils ./utils
COPY ./files ./files

ENTRYPOINT ["python","app.py"]