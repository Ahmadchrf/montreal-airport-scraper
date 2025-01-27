FROM python:3.9-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    libxss1 \
    fonts-liberation && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV CHROMEDRIVER_VERSION=131.0.6778.204
ENV CHROMEDRIVER_DIR=/chromedriver

RUN mkdir -p $CHROMEDRIVER_DIR && \
    wget -q --continue -P $CHROMEDRIVER_DIR "https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.204/linux64/chromedriver-linux64.zip" && \
    unzip $CHROMEDRIVER_DIR/chromedriver* -d $CHROMEDRIVER_DIR && \
    mv $CHROMEDRIVER_DIR/chromedriver-linux64/chromedriver $CHROMEDRIVER_DIR/ && \
    chmod +x $CHROMEDRIVER_DIR/chromedriver


ENV PATH=$CHROMEDRIVER_DIR:$PATH

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install python-dotenv

COPY ./scripts /opt/airflow/scripts
ENV PYTHONPATH=/opt/airflow
CMD ["python", "/opt/airflow/scripts/scraper.py"]