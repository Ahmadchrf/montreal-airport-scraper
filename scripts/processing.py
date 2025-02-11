from datetime import datetime, timezone, timedelta
import time
from minio import Minio
import json
import os
import psycopg2
import logging



MINIO_CLIENT = Minio(
    f"minio:9000",
    access_key=os.getenv('MINIO_ROOT_USER'),
    secret_key=os.getenv('MINIO_ROOT_PASSWORD'),
    secure=False
)

bucket_name = os.getenv('MINIO_DEFAULT_BUCKETS')

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv('FLIGHT_DB'),
        user=os.getenv('FLIGHT_USER'),
        password=os.getenv('FLIGHT_USER_PASSWORD'),
        host='postgres',
        port=5432
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transform_data(data):
    try:
        montreal_offset = timedelta(hours=-5)

        if data.get('creation_time'):
            creation_time = datetime.fromisoformat(data['creation_time']).replace(tzinfo=timezone.utc)
            data['schedule_date'] = (creation_time + montreal_offset).date()
        else:
            print("Invalid or missing creation_time")
            data['schedule_date'] = None

        if data.get('schedule_time') and data['schedule_time'] != 'Not found':
            time_part = datetime.strptime(data['schedule_time'], '%H:%M').time()
            data['schedule_time'] = datetime.combine(data['schedule_date'], time_part, tzinfo=timezone.utc) - montreal_offset
        else:
            print(f"Invalid or missing schedule_time: {data.get('schedule_time')}")
            data['schedule_time'] = None

        if data.get('revised_time') and data['revised_time'] != 'Not found':
            time_part = datetime.strptime(data['revised_time'].split('\n')[0], '%H:%M').time()
            data['revised_time'] = datetime.combine(data['schedule_date'], time_part, tzinfo=timezone.utc) - montreal_offset
        else:
            print(f"Invalid or missing revised_time: {data.get('revised_time')}")
            data['revised_time'] = None

        aircraft_parts = data.get('aircraft_comp', '').split(' ', 1)
        data['aircraft_number'] = aircraft_parts[0] if len(aircraft_parts) > 0 else "Unknown"
        data['aircraft_comp'] = aircraft_parts[1] if len(aircraft_parts) > 1 else "Unknown"

        destination_parts = data.get('destination', '').split(' (')
        data['destination'] = destination_parts[0].strip() if len(destination_parts) > 0 else "Unknown"
        data['destination_initial'] = destination_parts[1].strip(')') if len(destination_parts) > 1 else "Unknown"

        data['id_scrap'] = data.get('id', -1)

    except Exception as e:
        print(f"Error transforming data: {e}")
        raise

    return data


def sanitize_data(data):
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = value.encode('utf-8', 'replace').decode('utf-8')
    return data

def insert_data_into_db(data):
    insert_query = """
        INSERT INTO flight_schema.flight_table (
            schedule_time, schedule_date, revised_time, aircraft_number, aircraft_comp,
            aircraft_status, aircraft_gate, destination, destination_initial, id_scrap, creation_time
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    conn = get_db_connection()

    print("Transformed Data Before Insert:")
    for key, value in data.items():
        print(f"{key}: {repr(value)}")

    data = sanitize_data(data)

    cursor = conn.cursor()

    cursor.execute(insert_query, (
        data['schedule_time'], data['schedule_date'], data['revised_time'], data['aircraft_number'],
        data['aircraft_comp'], data['aircraft_status'], data['aircraft_gate'], data['destination'],
        data['destination_initial'], data['id_scrap'], data['creation_time']
    ))

    conn.commit()
    cursor.close()
    conn.close()

    
def download_and_process_files(folder_name):
    for obj in MINIO_CLIENT.list_objects(bucket_name, prefix=folder_name + '/', recursive=True):
        local_file_path = os.path.join('/tmp', obj.object_name.split('/')[-1])
        MINIO_CLIENT.fget_object(bucket_name, obj.object_name, local_file_path)

        with open(local_file_path, 'r') as f:
            data = json.load(f)
            transformed_data = transform_data(data)
            insert_data_into_db(transformed_data)
            print(f"Inserted data into database: {transformed_data}")

def get_latest_folder_name():
    folders = set()
    for obj in MINIO_CLIENT.list_objects(bucket_name, recursive=False):
        folder_name = obj.object_name.split('/')[0]
        folders.add(folder_name)

    try:
        latest_folder = sorted(
            folders, 
            key=lambda x: datetime.strptime(x, '%Y-%m-%d_%H-%M-%S')
        )[-1]
    except ValueError as e:
        raise Exception("Folder names are not in the expected format: YYYY-MM-DD_HH-MM-SS") from e

    return latest_folder


def main():
    logging.info("Starting the processor...")
    print("Waiting for the scraper to populate data")
    latest_folder_name = get_latest_folder_name()

    print(f"Processing latest folder: {latest_folder_name}")
    download_and_process_files(latest_folder_name)
    logging.info("Processing completed!")


if __name__ == "__main__":
    main()
