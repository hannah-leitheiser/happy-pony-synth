# Dockerfile

FROM ubuntu:20.04

# Install ffmpeg and other dependencies
RUN apt-get update && apt-get install -y ffmpeg && apt-get install -y libttspico-utils

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

# Set PYTHONPATH to include /app and /src
ENV PYTHONPATH /app:/src

ENTRYPOINT ["python", "main.py"]
