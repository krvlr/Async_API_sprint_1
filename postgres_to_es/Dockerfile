FROM python:3.10
WORKDIR /db_es_sync
COPY ./postgres_to_es .
RUN pip install -r requirements.txt
ENTRYPOINT python etl.py
