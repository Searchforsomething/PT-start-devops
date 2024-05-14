FROM python:3.9-alpine

RUN apk add --update build-base gcc postgresql-dev

COPY . .

RUN pip install -r requirements.txt --no-cache-dir


CMD ["python", "bot.py"]
