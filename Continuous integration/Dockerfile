# syntax=docker/dockerfile:1

FROM python:3.12-alpine

WORKDIR /app

COPY . .

RUN pip install flask werkzeug

EXPOSE 5000

CMD ["python", "app.py"]
