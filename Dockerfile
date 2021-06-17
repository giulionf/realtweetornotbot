FROM python:3.7-slim-buster

ENV VIRTUAL_ENV=./opt/venv

# Install tesseract and pip
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN apt update && apt install -y libsm6 libxext6
RUN apt-get -y install tesseract-ocr

# Create a working directory
COPY . /realtweetornotbot
WORKDIR /realtweetornotbot

# Install requirements in a venv
RUN python3 -m venv $VIRTUAL_ENV
COPY requirements.txt .
RUN . $VIRTUAL_ENV/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

# Load the Code
COPY ./src .
