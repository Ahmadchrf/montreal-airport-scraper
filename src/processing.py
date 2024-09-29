from datetime import datetime, timezone, timedelta
from minio import Minio
import json
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv() 

MINIO_CLIENT = Minio(
    f"localhost:{os.getenv('MINIO_PORT')}",
    access_key=os.getenv('MINIO_ROOT_USER'),
    secret_key=os.getenv('MINIO_ROOT_PASSWORD'),
    secure=False
)

bucket_name = os.getenv('MINIO_DEPARTURE_BUCKETS')

def get_latest_folder_name():
    folders = set()
    for obj in MINIO_CLIENT.list_objects(bucket_name, recursive=False):
        folder_name = obj.object_name.split('/')[0]
        folders.add(folder_name)

    latest_folder = sorted(folders, key=lambda x: datetime.strptime(x, '%Y-%m-%d_%H-%M-%S'))[-1]
    return latest_folder
def transform_data(data):
    data['schedule_time'] = data['schedule_time'].split('\n')[0]
    data['revised_time'] = data['revised_time'].split('\n')[0]
    data['destination'] = data['destination'].split('\n')[0]

    try:
        schedule_dt = datetime.strptime(data['schedule_time'], '%H:%M').replace(tzinfo=timezone.utc)
    except ValueError:
        schedule_dt = None
        print(f"Invalid schedule_time: {data['schedule_time']}")

    try:
        revised_dt = datetime.strptime(data['revised_time'], '%H:%M').replace(tzinfo=timezone.utc)
    except ValueError:
        revised_dt = None
        print(f"Invalid revised_time: {data['revised_time']}")

    if schedule_dt:
        montreal_offset = timedelta(hours=-4)
        data['utc_time'] = schedule_dt.isoformat()
        data['montreal_time'] = (schedule_dt + montreal_offset).isoformat()

        if revised_dt:
            data['time_difference'] = str(schedule_dt - revised_dt)
        else:
            data['time_difference'] = "N/A"
    else:
        data['utc_time'] = "N/A"
        data['montreal_time'] = "N/A"
        data['time_difference'] = "N/A"

    return data

def download_and_process_files(folder_name, chunk_size=10):
    local_folder_path = os.path.join(os.getcwd(), folder_name)
    os.makedirs(local_folder_path, exist_ok=True)

    files_processed = 0
    file_list = []
    combined_data = []

    for obj in MINIO_CLIENT.list_objects(bucket_name, prefix=folder_name + '/', recursive=True):
        file_list.append(obj)
        if len(file_list) == chunk_size:
            for file_obj in file_list:
                local_file_path = os.path.join(local_folder_path, file_obj.object_name.split('/')[-1])
                MINIO_CLIENT.fget_object(bucket_name, file_obj.object_name, local_file_path)

                with open(local_file_path, 'r') as f:
                    data = json.load(f)
                    transformed_data = transform_data(data)
                    combined_data.append(transformed_data)

                files_processed += 1

            file_list = []

            df = pd.DataFrame(combined_data)
            csv_file_name = f"data_exported_chunk_{files_processed//chunk_size}.csv"
            df.to_csv(csv_file_name, index=False)
            print(f"Processed {files_processed} files. Exported to {csv_file_name}")

            combined_data = []

def main():
    latest_folder_name = get_latest_folder_name()
    print(f"Latest folder: '{latest_folder_name}'")
    download_and_process_files(latest_folder_name)

if __name__ == "__main__":
    main()
