from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

CHROME_DRIVER_PATH = r'C:\Users\ahmad\OneDrive\Bureau\chromedriver.exe'

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

service = Service(executable_path=CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.google.com")
print(driver.title)

driver.quit()
