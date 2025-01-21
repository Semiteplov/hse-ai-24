FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ARG BOT_TOKEN
ARG OPEN_WEATHER_TOKEN

ENV BOT_TOKEN=$BOT_TOKEN
ENV OPEN_WEATHER_TOKEN=$OPEN_WEATHER_TOKEN

CMD ["python", "main.py"]