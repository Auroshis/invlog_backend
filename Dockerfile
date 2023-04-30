FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

ENV PYTHONUNBUFFERED True

COPY . /app
WORKDIR /app

RUN pip install pymongo

ENV MONGODB_URL=mongodb+srv://mongoinvlog:LVyIX2yP1wXF60LT@invlogcluster0.5fksgid.mongodb.net/?retryWrites=true&w=majority
ENV MONGODB_DB=InvlogDB

EXPOSE 8000

ENTRYPOINT uvicorn app:app --port $PORT --host 0.0.0.0
