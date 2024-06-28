# Dockerfile

FROM python:3.9-slim

# Install ffmpeg and other dependencies
RUN apt-get update && apt-get install -y ffmpeg

COPY . .

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app

# Install git (if not already installed) and clone python3-midi repository
RUN apt-get update && \
    apt-get install -y git && \
    git clone https://github.com/louisabraham/python3-midi.git /app/python3-midi

# Change into the python3-midi directory
WORKDIR /app/python3-midi

# Install the midi library using setup.py
RUN python setup.py install

WORKDIR /app

ENTRYPOINT ["python", "main.py"]
