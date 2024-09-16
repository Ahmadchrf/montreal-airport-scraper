import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from constants import web_site_url

chromedriver_path = r"C:\Users\ahmad\OneDrive\Bureau\chromedriver.exe"

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

service = Service(executable_path=chromedriver_path)
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

for row_index in range(1, 11):
    xpath_schedule = f'//*[@id="DataTables_Table_0"]/tbody/tr[{row_index}]/td[1]/time'
    xpath_revised = f'//*[@id="DataTables_Table_0"]/tbody/tr[{row_index}]/td[2]/time'


    xpath_aircraft_comp_img = f'//*[@id="DataTables_Table_0"]/tbody/tr[{row_index}]/td[3]/img'


    xpath_aircraft = f'//*[@id="DataTables_Table_0"]/tbody/tr[{row_index}]/td[4]'
    xpath_destination = f'//*[@id="DataTables_Table_0"]/tbody/tr[{row_index}]/td[5]'
    xpath_state = f'//*[@id="DataTables_Table_0"]/tbody/tr[{row_index}]/td[6]'
    xpath_gate = f'//*[@id="DataTables_Table_0"]/tbody/tr[{row_index}]/td[7]'

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
    
    try:
        state_element = driver.find_element(By.XPATH, xpath_state)
        data['state'] = state_element.text.strip()
    except NoSuchElementException:
        data['state'] = "Not found"

    try:
        gate_element = driver.find_element(By.XPATH, xpath_gate)
        data['gate'] = gate_element.text.strip()
    except NoSuchElementException:
        data['gate'] = "Not found"

    data['id'] = row_index
    data['creation_time'] = datetime.now().isoformat()

    with open(f'row_{row_index}.json', 'w') as f:
        json.dump(data, f, indent=4)

driver.quit()
print("Data saved to JSON files.")