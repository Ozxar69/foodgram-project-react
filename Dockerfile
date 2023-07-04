FROM python:3.9-slim

WORKDIR /app

COPY backend_foodgram/requirements.txt ./

RUN pip3 install -r requirements.txt --no-cache-dir

COPY backend_foodgram ./

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]