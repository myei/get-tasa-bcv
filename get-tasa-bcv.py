#!/usr/bin/env python3.9 -u

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from locale import setlocale, atof, LC_ALL
from sys import argv


PARAMETERS = {
    "bcv_url": "https://www.bcv.org.ve/",
    "rate_field": "dolar",
    "browser": {
        "drivers": [webdriver.Chrome, webdriver.Firefox],
        "optionsHandler": [ChromeOptions, FirefoxOptions],
        "size": "--window-size=1920,1080",
        "mode": "--private-window",
        "visibility": "--headless",
        "availables": {
            "-c": 0,
            "-f": 1 
        }
    }
}

DRIVER_TO_USE = 0
if len(argv) > 1 and argv[1] in list(PARAMETERS["browser"]["availables"].keys()):
    DRIVER_TO_USE = PARAMETERS["browser"]["availables"][argv[1]]

print("Utilizando Firefox..." if DRIVER_TO_USE == 1 else "Utilizando chrome...")

print("Consultando tasa de cambio en: ", PARAMETERS["bcv_url"])

setlocale(LC_ALL, "")

options = PARAMETERS["browser"]["optionsHandler"][DRIVER_TO_USE]()
options.add_argument(PARAMETERS["browser"]["visibility"])

if DRIVER_TO_USE == PARAMETERS["browser"]["availables"]["-c"]:
    options.add_argument(PARAMETERS["browser"]["size"])
    options.add_argument(PARAMETERS["browser"]["mode"])
else:
    options.add_argument("--width=2560")
    options.add_argument("--height=1440")

driver = PARAMETERS["browser"]["drivers"][DRIVER_TO_USE](options=options)
driver.get(PARAMETERS["bcv_url"])

target = driver.find_element(By.ID, PARAMETERS["rate_field"])
rate = round(atof((target.text.split("\n")[1])), 2)

print("Tasa $:", rate)

driver.close()
