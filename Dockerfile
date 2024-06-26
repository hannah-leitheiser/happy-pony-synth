# Dockerfile

FROM python:3.9-slim

# Install ffmpeg and other dependencies
RUN apt-get update && apt-get install -y ffmpeg

COPY . .

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app

CMD ["python", "main.py"]
