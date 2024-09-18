FROM python:3.10.12-slim-buster

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        nano \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app
COPY . .

COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["python3","-m", "src.scraper"]