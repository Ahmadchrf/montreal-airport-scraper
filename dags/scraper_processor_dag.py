from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import pendulum
import os


local_tz = pendulum.timezone("America/Montreal")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

MINIO_ENV = {
    "MINIO_ROOT_USER": Variable.get("MINIO_ROOT_USER", default_var="AhmadUser"),
    "MINIO_ROOT_PASSWORD": Variable.get("MINIO_ROOT_PASSWORD", default_var="AhmadPasswoRd"),
    "MINIO_DEFAULT_BUCKETS": Variable.get("MINIO_DEFAULT_BUCKETS", default_var="dev-raw-scraper-mtl"),
}


with DAG(
    dag_id='scraper_processor_pipeline',
    default_args=default_args,
    schedule_interval="*/30 * * * *",
    start_date=datetime(2025, 2, 2, 14, 0, tzinfo=local_tz),
    catchup=False
) as dag:

    scraper_task = DockerOperator(
        task_id='run_scraper',
        image='scraper_image',
        container_name='scraper_container_run',
        api_version='auto',
        auto_remove=True,
        docker_url='unix://var/run/docker.sock',
        network_mode='montreal-airport-scraper_airflow-network',
        command="python /opt/airflow/scripts/scraper.py",
        environment={
            "MINIO_ROOT_USER": os.getenv('MINIO_ROOT_USER'),
            "MINIO_ROOT_PASSWORD": os.getenv('MINIO_ROOT_PASSWORD'),
            "MINIO_DEFAULT_BUCKETS": os.getenv('MINIO_DEFAULT_BUCKETS')
        }
    )

    processor_task = DockerOperator(
        task_id='run_processing',
        image='processor_image',
        container_name='processing_container_run',
        api_version='auto',
        auto_remove=True,
        docker_url='unix://var/run/docker.sock',
        network_mode='montreal-airport-scraper_airflow-network',
        command="python /opt/airflow/scripts/processing.py",
        environment={
            "MINIO_ROOT_USER": os.getenv('MINIO_ROOT_USER'),
            "MINIO_ROOT_PASSWORD": os.getenv('MINIO_ROOT_PASSWORD'),
            "MINIO_DEFAULT_BUCKETS": os.getenv('MINIO_DEFAULT_BUCKETS')
        }
    )

    scraper_task >> processor_task