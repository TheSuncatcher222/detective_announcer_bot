FROM python:3.11-slim

LABEL description="Detective Announcer Bot" \
      version="1.0" \
      maintainer="TheSuncatcher222" \
      deployer="https://github.com/TheSuncatcher222"

RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir
