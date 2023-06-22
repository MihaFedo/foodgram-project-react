FROM python:3.7-slim

WORKDIR /app

COPY ./infra/requirements.txt .

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY ./backend/foodgram/ .

# COPY ././data ./data 

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]