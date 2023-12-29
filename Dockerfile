FROM python:latest

WORKDIR /app/

RUN python -m pip install --upgrade pip

RUN python -m pip install praw

RUN python -m pip install python-decouple

COPY main.py /app/

COPY config.py /app/

COPY .env /app/

CMD ["python", "main.py"]