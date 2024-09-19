import time
import json
from datetime import datetime
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from minio import Minio
from dotenv import load_dotenv

load_dotenv()

from constants import web_site_url


client=Minio(
    f"minio:{os.getenv('MINIO_PORT')}",
    access_key=os.getenv('MINIO_ROOT_USER'),
    secret_key=os.getenv('MINIO_ROOT_PASSWORD'),
)


bucket_name = os.getenv('MINIO_DEFAULT_BUCKETS')
current_date = datetime.now().strftime('%Y-%m-%d')
folder_path = f"{current_date}/"



options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')


project_root = os.path.dirname(__file__)
# CHROMEDRIVER_PATH = os.path.join(project_root, 'drivers', 'chromedriver.exe')
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', '/usr/local/bin/chromedriver')

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

for row_index in range(1, 3):
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

    clean_creation_time = data['creation_time'].replace(':', '-').replace('T', '_').split('.')[0]
    filename = f'event_departure_{clean_creation_time}.json'

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)

    json_filename = f"{folder_path}event_departure_{clean_creation_time}.json"
    client.fput_object(bucket_name, json_filename, filename)


driver.quit()
print("Data saved to JSON files.")