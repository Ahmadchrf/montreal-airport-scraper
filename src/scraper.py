import time
import json
from datetime import datetime
import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from minio import Minio

from src.constants import WEB_SITE_URL, CHROME_DRIVER_PATH


MINIO_CLIENT = Minio(
    f"minio:9000",
    access_key=os.getenv('MINIO_ROOT_USER'),
    secret_key=os.getenv('MINIO_ROOT_PASSWORD'),
    secure=False
)

bucket_name = os.getenv('MINIO_DEFAULT_BUCKETS')

print(f"Bucket name from environment: {bucket_name}")
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
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.204 Safari/537.36")


    service = Service(executable_path=CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(WEB_SITE_URL)

    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="didomi-notice-agree-button"]'))
        )
        accept_button.click()
        print("Accept Button clicked.")

        opinion_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div[5]/div[2]/div/div[3]/button[2]'))
        )
        opinion_button.click()
        print("Opinion Button clicked.")

    except Exception as e:
        print(f"No pop-up found or button not clickable: {e}")


    local_folder_path = os.path.join(os.getcwd(), new_folder_name)
    os.makedirs(local_folder_path, exist_ok=True)

    driver.save_screenshot("headless_debug_beginning.png")

    for row_index in range(1,11):
        xpath_schedule      = f'//*[@id="main"]/webruntime-app/lwr-router-container/webruntime-inner-app/dxp_data_provider-user-data-provider/dxp_data_provider-data-proxy/c-osf-a-d-m-custom-theme/div/section/slot/webruntime-router-container/dxp_data_provider-user-data-provider/dxp_data_provider-data-proxy/community_layout-slds-flexible-layout/div/community_layout-section[2]/div[3]/community_layout-column/div/c-osf-flights-listings/div/div[2]/div[1]/div[{row_index}]/div[1]/span'                       
        xpath_revised       = f'//*[@id="main"]/webruntime-app/lwr-router-container/webruntime-inner-app/dxp_data_provider-user-data-provider/dxp_data_provider-data-proxy/c-osf-a-d-m-custom-theme/div/section/slot/webruntime-router-container/dxp_data_provider-user-data-provider/dxp_data_provider-data-proxy/community_layout-slds-flexible-layout/div/community_layout-section[2]/div[3]/community_layout-column/div/c-osf-flights-listings/div/div[2]/div[1]/div[{row_index}]/div[1]'
        xpath_aircraft_comp = f'//*[@id="main"]/webruntime-app/lwr-router-container/webruntime-inner-app/dxp_data_provider-user-data-provider/dxp_data_provider-data-proxy/c-osf-a-d-m-custom-theme/div/section/slot/webruntime-router-container/dxp_data_provider-user-data-provider/dxp_data_provider-data-proxy/community_layout-slds-flexible-layout/div/community_layout-section[2]/div[3]/community_layout-column/div/c-osf-flights-listings/div/div[2]/div[1]/div[{row_index}]/div[2]/div[1]'
        xpath_status        = f'//*[@id="main"]/webruntime-app/lwr-router-container/webruntime-inner-app/dxp_data_provider-user-data-provider/dxp_data_provider-data-proxy/c-osf-a-d-m-custom-theme/div/section/slot/webruntime-router-container/dxp_data_provider-user-data-provider/dxp_data_provider-data-proxy/community_layout-slds-flexible-layout/div/community_layout-section[2]/div[3]/community_layout-column/div/c-osf-flights-listings/div/div[2]/div[1]/div[{row_index}]/div[3]/div[1]/span[1]/span'
        xpath_destination   = f'//*[@id="main"]/webruntime-app/lwr-router-container/webruntime-inner-app/dxp_data_provider-user-data-provider/dxp_data_provider-data-proxy/c-osf-a-d-m-custom-theme/div/section/slot/webruntime-router-container/dxp_data_provider-user-data-provider/dxp_data_provider-data-proxy/community_layout-slds-flexible-layout/div/community_layout-section[2]/div[3]/community_layout-column/div/c-osf-flights-listings/div/div[2]/div[1]/div[{row_index}]/div[2]/div[2]'             
        xpath_gate          = f'//*[@id="main"]/webruntime-app/lwr-router-container/webruntime-inner-app/dxp_data_provider-user-data-provider/dxp_data_provider-data-proxy/c-osf-a-d-m-custom-theme/div/section/slot/webruntime-router-container/dxp_data_provider-user-data-provider/dxp_data_provider-data-proxy/community_layout-slds-flexible-layout/div/community_layout-section[2]/div[3]/community_layout-column/div/c-osf-flights-listings/div/div[2]/div[1]/div[{row_index}]/div[3]/div[1]/span[2]/span'
        
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
            aircraft_comp_img = driver.find_element(By.XPATH, xpath_aircraft_comp)
            data['aircraft_comp'] = aircraft_comp_img.text.strip()
        except NoSuchElementException:
            data['aircraft_comp'] = "Not found"

        try:
            aircraft_element = driver.find_element(By.XPATH, xpath_status)
            data['aircraft_status'] = aircraft_element.text.strip()
        except NoSuchElementException:
            data['aircraft_status'] = "Not found"

        try:
            gate = driver.find_element(By.XPATH, xpath_gate)
            data['aircraft_gate'] = gate.text.strip()
        except NoSuchElementException:
            data['aircraft_gate'] = "Not found"

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


    driver.save_screenshot("headless_debug_end.png")
    driver.quit()
    print("Data saved to JSON files.")

if __name__ == "__main__":
    main()
