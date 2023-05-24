FROM python:3.9

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED True

WORKDIR /openai_webhook

ENV PORT 8080

COPY . /openai_webhook

EXPOSE 8080

RUN pip install -r requirements.txt

CMD exec gunicorn --bind :$PORT run:app



