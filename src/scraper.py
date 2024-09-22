import time
import json
from datetime import datetime
import os
from dotenv import load_dotenv 

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from minio import Minio

from constants import web_site_url

load_dotenv() 


MINIO_CLIENT = Minio(
    f"localhost:{os.getenv('MINIO_PORT')}",
    access_key=os.getenv('MINIO_ROOT_USER'),
    secret_key=os.getenv('MINIO_ROOT_PASSWORD'),
    secure=False
)

bucket_name = os.getenv('MINIO_DEFAULT_BUCKETS')
current_date = datetime.now().strftime('%Y-%m-%d')

def get_new_folder_name():
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    new_folder_name = current_time
    return new_folder_name


def main():
    if not MINIO_CLIENT.bucket_exists(bucket_name):
        MINIO_CLIENT.make_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' created.")
    else:
        print(f"Bucket '{bucket_name}' already exists.")

    new_folder_name = get_new_folder_name()
    print(f"New folder name: '{new_folder_name}'")

    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    CHROME_DRIVER_PATH = r'C:\Users\ahmad\OneDrive\Bureau\chromedriver.exe'
    service = Service(executable_path=CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(web_site_url)

    try:
        time.sleep(3)
        accept_button_xpath = '//*[@id="didomi-notice-agree-button"]'
        accept_button = driver.find_element(By.XPATH, accept_button_xpath)
        accept_button.click()
        print("Pop-up accepted.")
    except NoSuchElementException:
        print("No pop-up found or button not clickable")

    local_folder_path = os.path.join(os.getcwd(), new_folder_name)
    os.makedirs(local_folder_path, exist_ok=True)

    for row_index in range(1, 13):
        xpath_schedule = f'//*[@id="DataTables_Table_0"]/tbody/tr[{row_index}]/td[1]/time'
        xpath_revised = f'//*[@id="DataTables_Table_0"]/tbody/tr[{row_index}]/td[2]/time'
        xpath_aircraft_comp_img = f'//*[@id="DataTables_Table_0"]/tbody/tr[{row_index}]/td[3]/img'
        xpath_aircraft = f'//*[@id="DataTables_Table_0"]/tbody/tr[{row_index}]/td[4]'
        xpath_destination = f'//*[@id="DataTables_Table_0"]/tbody/tr[{row_index}]/td[5]'

        time.sleep(2)
        data = {}

        try:
            flight_time_element = driver.find_element(By.XPATH, xpath_schedule)
            data['schedule_time'] = flight_time_element.text.strip()
        except NoSuchElementException:
            data['schedule_time'] = "Not found"

        try:
            revised_element = driver.find_element(By.XPATH, xpath_revised)
            data['revised_time'] = revised_element.text.strip()
        except NoSuchElementException:
            data['revised_time'] = "Not found"

        try:
            aircraft_comp_img = driver.find_element(By.XPATH, xpath_aircraft_comp_img)
            data['aircraft_comp'] = aircraft_comp_img.get_attribute('alt').strip()
        except NoSuchElementException:
            data['aircraft_comp'] = "Not found"

        try:
            aircraft_element = driver.find_element(By.XPATH, xpath_aircraft)
            data['aircraft_number'] = aircraft_element.text.strip()
        except NoSuchElementException:
            data['aircraft_number'] = "Not found"

        try:
            destination_element = driver.find_element(By.XPATH, xpath_destination)
            data['destination'] = destination_element.text.strip()
        except NoSuchElementException:
            data['destination'] = "Not found"


        data['id'] = row_index
        data['creation_time'] = datetime.now().isoformat()

        existing_files = len([name for name in os.listdir(local_folder_path) if os.path.isfile(os.path.join(local_folder_path, name))])
        filename = f'event_departure_{existing_files + 1}.json'

        local_file_path = os.path.join(local_folder_path, filename)

        with open(local_file_path, 'w') as f:
            json.dump(data, f, indent=4)

        json_minio_path = f"{new_folder_name}/{filename}"
        MINIO_CLIENT.fput_object(bucket_name, json_minio_path, local_file_path)
        print(f"File '{filename}' uploaded to MinIO bucket '{bucket_name}' in folder '{new_folder_name}'.")

    driver.quit()
    print("Data saved to JSON files.")

if __name__ == "__main__":
    main()
