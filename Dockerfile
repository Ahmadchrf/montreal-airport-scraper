FROM python:3.10.12-slim-buster

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        nano \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
&& apt install ./google-chrome-stable_current_amd64.deb

RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip


WORKDIR /app
COPY . .

COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir

ENV CHROME_DRIVER_PATH="/usr/local/bin/chromedriver"

CMD ["python3","-m", "src.scraper"]