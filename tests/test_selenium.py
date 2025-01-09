from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

CHROME_DRIVER_PATH = "/chromedriver/chromedriver"

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')


service = Service(executable_path=CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.google.com")
print(driver.title)

driver.quit()
