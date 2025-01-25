from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime, timedelta
import pendulum

local_tz = pendulum.timezone("America/Montreal")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='scraper_processor_pipeline',
    default_args=default_args,
    schedule_interval='*/15 * * * *',
    start_date=datetime(2025, 1, 25, 15, 45, tzinfo=local_tz),
    catchup=False
) as dag:

    run_scraper = DockerOperator(
        task_id='run_scraper',
        image='montreal-scraper:latest',
        container_name='airflow_scraper',
        auto_remove=True,
        environment={
            'MINIO_ROOT_USER': '{{ var.value.MINIO_ROOT_USER }}',
            'MINIO_ROOT_PASSWORD': '{{ var.value.MINIO_ROOT_PASSWORD }}',
            'MINIO_DEFAULT_BUCKETS': '{{ var.value.MINIO_DEFAULT_BUCKETS }}',
        },
        network_mode='airflow-network',  
    )

    run_processor = DockerOperator(
        task_id='run_processor',
        image='montreal-processor:latest',
        container_name='airflow_processor',
        auto_remove=True,
        environment={
            'MINIO_ROOT_USER': '{{ var.value.MINIO_ROOT_USER }}',
            'MINIO_ROOT_PASSWORD': '{{ var.value.MINIO_ROOT_PASSWORD }}',
            'MINIO_DEFAULT_BUCKETS': '{{ var.value.MINIO_DEFAULT_BUCKETS }}',
            'POSTGRES_USER': '{{ var.value.POSTGRES_USER }}',
            'POSTGRES_PASSWORD': '{{ var.value.POSTGRES_PASSWORD }}',
            'POSTGRES_DB': '{{ var.value.POSTGRES_DB }}',
        },
        execution_timeout=timedelta(minutes=2),
        network_mode='airflow-network',  
    )

    run_scraper >> run_processor