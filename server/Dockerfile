FROM python:3.8

RUN pip install flask gunicorn python-binance binance Werkzeug google-cloud google-cloud-secret-manager firebase-admin

COPY src/ app/
WORKDIR /app

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app