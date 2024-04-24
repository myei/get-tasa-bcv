from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from locale import setlocale, atof, LC_ALL

PARAMETERS = {
    "bcv_url": "https://www.bcv.org.ve/",
    "rate_field": "dolar",
    "browser": {
        "size": "--window-size=1920,1080",
        "mode": "--private-window",
        "visibility": "--headless"
    }

}


setlocale(LC_ALL, '')

options = Options()
options.add_argument(PARAMETERS['browser']['size'])
options.add_argument(PARAMETERS['browser']['mode'])
options.add_argument(PARAMETERS['browser']['visibility'])

driver = webdriver.Chrome(options=options)
driver.get(PARAMETERS['bcv_url'])

target = driver.find_element(By.ID, PARAMETERS['rate_field'])
rate = round(atof((target.text.split('\n')[1])), 2)

print("Tasa $:", rate)

driver.close()
