FROM python:3.8-slim

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


COPY ./src /app/src

RUN pip install python-dotenv
ENV PYTHONPATH=/app
CMD ["python3", "-m", "src.scraper"]