FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY . /app
WORKDIR /app

RUN pip install pymongo

ENV MONGODB_URL=mongodb+srv://mongoinvlog:LVyIX2yP1wXF60LT@invlogcluster0.5fksgid.mongodb.net/?retryWrites=true&w=majority
ENV MONGODB_DB=InvlogDB

EXPOSE 80

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
