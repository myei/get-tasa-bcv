#!/usr/bin/env python3.9 -u

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException, SessionNotCreatedException, TimeoutException
from locale import setlocale, atof, LC_ALL
from sys import argv
from datetime import date
import sqlite3, os, warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message="The Python dbus package is not installed")

if '-h' in argv:
    print('usage: python get-tasa-bcv.py [options] \n')
    print('options:')
    print('  -c      Google Chrome (default driver)')
    print('  -f      Mozilla Firefox')
    print('  -s      Short printed')
    print('  -u      Get only USD (dolar) rate')
    print('  -e      Get only EUR (euro) rate')
    print('  -n      Generates notification on screen')
    print('  -h      Show this help')
    exit(0)

DRIVER_TO_USE = 1 if '-f' in argv else 0
IS_SHORT_PRINTED = '-s' in argv
NOTIFICATION = '-n' in argv

setlocale(LC_ALL, "")

PARAMETERS = {
        "bcv_url": "https://www.bcv.org.ve/",
        "rate_field": ["dolar", "euro"],
        "db_file": "bcv_rates.db",
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

class DatabaseManager:
    def __init__(self, db_file):
        self.db_file = db_file
        self._connection = None
    
    def get_connection(self):
        if self._connection is None:
            try:
                self._connection = sqlite3.connect(self.db_file)
                self._connection.row_factory = sqlite3.Row 
            except sqlite3.Error as e:
                print(f"Error al conectar con la base de datos: {e}")
                return None
        return self._connection
    
    def execute_query(self, query, params=None, fetch_one=False):
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = cursor.fetchone() if fetch_one else cursor.fetchall()
            conn.commit()
            return result
        except sqlite3.Error as e:
            print(f"Error en consulta de base de datos: {e}")
            return None
    
    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None

class RatesDao:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.init_database()
    
    def init_database(self):
        query = '''
            CREATE TABLE IF NOT EXISTS exchange_rates (
                date TEXT PRIMARY KEY,
                usd_rate REAL,
                eur_rate REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
        self.db_manager.execute_query(query)
        
        index_query = '''
            CREATE INDEX IF NOT EXISTS idx_exchange_rates_date 
            ON exchange_rates(date)
        '''
        self.db_manager.execute_query(index_query)

    def get_cached_rates(self, target_date):
        query = "SELECT usd_rate, eur_rate FROM exchange_rates WHERE date = ?"
        cached_data = self.db_manager.execute_query(query, (target_date,), fetch_one=True)

        if not cached_data:
            return None
        
        return list(cached_data)

    def save_rates_to_db(self, target_date, rates):
        currency_map = {"dolar": "usd_rate", "euro": "eur_rate"}
        rate_values = {"usd_rate": None, "eur_rate": None}
        
        for i, currency_id in enumerate(PARAMETERS["rate_field"]):
            if currency_id in currency_map:
                rate_values[currency_map[currency_id]] = rates[i]
        
        query = "INSERT OR REPLACE INTO exchange_rates (date, usd_rate, eur_rate) VALUES (?, ?, ?)"
        self.db_manager.execute_query(query, (target_date, rate_values["usd_rate"], rate_values["eur_rate"]))

class WebDriverManager:
    driver = None
    
    def __init__(self):
        self.create_webdriver()

    def create_webdriver(self):
        options = PARAMETERS["browser"]["optionsHandler"][DRIVER_TO_USE]()
        options.add_argument(PARAMETERS["browser"]["visibility"])

        if DRIVER_TO_USE == PARAMETERS["browser"]["availables"]["-c"]: 
            options.add_argument(PARAMETERS["browser"]["size"])
            options.add_argument(PARAMETERS["browser"]["mode"])
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
        else: 
            options.add_argument("--width=2560")
            options.add_argument("--height=1440")
            options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0")

        try:
            self.driver = PARAMETERS["browser"]["drivers"][DRIVER_TO_USE](options=options)
            
            # Configurar timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            if DRIVER_TO_USE == PARAMETERS["browser"]["availables"]["-c"]:
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        except (WebDriverException, SessionNotCreatedException) as e:
            browser_name = "Firefox" if DRIVER_TO_USE == 1 else "Chrome"
            error_msg = str(e).lower()
            
            if "chromedriver" in error_msg or "geckodriver" in error_msg or "executable" in error_msg:
                print(f"Error: No se encontró el WebDriver de {browser_name}.")
                print(f"Instala el WebDriver correspondiente:")
                if DRIVER_TO_USE == 0:
                    print(f"  - Descarga ChromeDriver desde: https://chromedriver.chromium.org/")
                else:
                    print(f"  - Descarga GeckoDriver desde: https://github.com/mozilla/geckodriver/releases")
                print(f"  - Asegúrate de que esté en el PATH del sistema")
            else:
                print(f"Error: No se pudo inicializar el navegador {browser_name}.")
                print(f"Verifica que {browser_name} esté instalado correctamente.")
            
            print(f"Detalles técnicos: {str(e)}")
            exit(1)
    
    def get_element_text(self, by, value):
        try:
            wait = WebDriverWait(self.driver, 15)
            # Esperar a que el elemento esté presente y visible
            target = wait.until(EC.presence_of_element_located((by, value)))
            
            # Esperar a que el elemento tenga contenido
            wait.until(lambda d: target.text.strip() != "")
            
            # Validar que el elemento tenga contenido
            element_text = target.text.strip()
            return element_text
        except NoSuchElementException:
            return None
    
    def get_page_title(self):
        return self.driver.title.lower()


class RatesScraper:
    def __init__(self):
        self.db_manager = DatabaseManager(PARAMETERS["db_file"])
        self.rates_dao = RatesDao(self.db_manager)
        self.driver_manager = WebDriverManager()
        self.date = None
        self.rates = None
        self.notification = True if '-n' in argv else False

        self.set_rates()

    def set_rates(self):
        self.date = date.today().isoformat()
        self.rates = self.rates_dao.get_cached_rates(self.date)

        if not self.rates:
            self.rates = self.scrape_rates()
    
    def _filter_rates_by_currency(self):
        if '-u' in argv:
            return [self.rates[0]], ["Dólar"]
        elif '-e' in argv:
            return [self.rates[1]], ["Euro"]
        else:
            return self.rates, ["Dólar", "Euro"]
    
    def get_rates_short(self):
        rates, _ = self._filter_rates_by_currency()

        for rate in rates:
            print(rate)
    
    def get_rates_beauty(self):
        print("Utilizando Firefox..." if DRIVER_TO_USE == 1 else "Utilizando chrome...")
        print("Consultando tasa de cambio en: ", PARAMETERS["bcv_url"])

        rates, currencies = self._filter_rates_by_currency()
        _rates=""

        for rate, currency in zip(rates, currencies):
            _rates += "".join(["Tasa ", currency, ": ", str(rate), "\n"])

        print(f"{_rates}")

        
            
    def scrape_rates(self):
        try:
            self.driver_manager.driver.get(PARAMETERS["bcv_url"])
            
            # verificar si la página fue bloqueada
            if "blocked" in self.driver_manager.get_page_title() or "access denied" in self.driver_manager.get_page_title():
                raise ValueError(f"El sitio web bloqueó el acceso. Título de página: '{self.driver_manager.get_page_title()}'")
            
            rates = []
            
            for currency_id in PARAMETERS["rate_field"]:
                element_text = self.driver_manager.get_element_text(By.ID, currency_id)
                if not element_text:
                    raise ValueError(f"El elemento de tasa para {currency_id} está vacío")
                
                # Procesar el texto para extraer la tasa
                text_lines = element_text.split("\n")
                if len(text_lines) < 2:
                    raise ValueError(f"Formato inesperado del elemento {currency_id}: '{element_text}'")
                
                rate = round(atof(text_lines[1]), 2)
                rates.append(rate)
            
            self.rates_dao.save_rates_to_db(self.date, rates)

            return rates
            
        except NoSuchElementException:
            print("Error: No se pudo encontrar el elemento con la tasa de cambio en la página del BCV.")
            print("Es posible que la estructura de la página haya cambiado.")
            print(f"Buscando elemento con ID: '{PARAMETERS['rate_field']}'")
            exit(1)
        except ValueError as e:
            print(f"Error: Problema al procesar los datos de la tasa de cambio.")
            print(f"Detalles: {str(e)}")
            exit(1)
        except TimeoutException:
            print("Error: Tiempo de espera agotado al cargar la página del BCV.")
            print("Verifica tu conexión a internet e intenta nuevamente.")
            exit(1)
        except Exception as e:
            print(f"Error inesperado al procesar la tasa de cambio: {str(e)}")
            exit(1)
        finally:
            try:
                if self.driver_manager and self.driver_manager.driver:
                    self.driver_manager.driver.quit()
            except:
                pass
            finally:
                self.db_manager.close()

    def show_notification(self):
        try:
            from plyer import notification
        
            message = f"💵 Tasa Dólar: {self.rates[0]} | 💶 Tasa Euro: {self.rates[1]}"
            
            notification.notify(
                title='💰 Tasas BCV Actualizadas 📈',
                message=message,
                app_name='get-tasa-bcv',
                timeout=10
            )
        except ImportError:
            print("⚠️  plyer no instalado. Usa: pip3 install plyer")
        except Exception as e:
            print(f"Error en notificación: {e}")

if IS_SHORT_PRINTED:
    RatesScraper().get_rates_short()
elif NOTIFICATION:
    RatesScraper().show_notification()
else:
    RatesScraper().get_rates_beauty()
