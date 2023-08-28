# syntax=docker/dockerfile:1
FROM python:3.11.5-slim-bullseye
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /var/web
COPY requirements.txt .
RUN pip install -r requirements.txt