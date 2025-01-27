from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime, timedelta
import pendulum
import subprocess

local_tz = pendulum.timezone("America/Montreal")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='scraper_processor_pipeline',
    default_args=default_args,
    schedule_interval='*/15 * * * *',
    start_date=datetime(2025, 1, 26, 12, 0, tzinfo=local_tz),
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
            "MINIO_ROOT_USER": "AhmadUser",
            "MINIO_ROOT_PASSWORD": "AhmadPasswoRd",
            "MINIO_DEFAULT_BUCKETS": "dev-raw-scraper-mtl"
        }
    )

    processor_task = DockerOperator(
        task_id='run_procesing',
        image='processor_image',
        container_name='processing_container_run',
        api_version='auto',
        auto_remove=True,
        docker_url='unix://var/run/docker.sock',
        network_mode='montreal-airport-scraper_airflow-network',
        command="python /opt/airflow/scripts/processing.py",
        environment={
            "MINIO_ROOT_USER": "AhmadUser",
            "MINIO_ROOT_PASSWORD": "AhmadPasswoRd",
            "MINIO_DEFAULT_BUCKETS": "dev-raw-scraper-mtl"
        }
    )

    scraper_task >> processor_task