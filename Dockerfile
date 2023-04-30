FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

ENV PYTHONUNBUFFERED True

COPY . /app
WORKDIR /app

RUN pip install pymongo

ENV MONGODB_URL=$MONGODB_URL
ENV MONGODB_DB=$MONGODB_DB

EXPOSE 8000

ENTRYPOINT uvicorn app:app --port $PORT --host 0.0.0.0
