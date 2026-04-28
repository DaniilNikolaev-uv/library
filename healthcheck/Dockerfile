FROM python:3.12

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends docker.io \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8085

COPY . .

CMD [ "python", "server.py" ]
