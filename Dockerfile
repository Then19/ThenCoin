FROM python:3.9-slim

WORKDIR /app
EXPOSE 80

ENV SENTRY_DSN="" \
    POSTGRESQL_DSN="" \
    CLICKHOUSE_DSN=""

COPY ./requirements.txt /app/
RUN python -m pip install --upgrade pip

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["alembic", "upgrade", "head"]
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "80"]