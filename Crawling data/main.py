import pandas as pd
import os
import shutil
import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

browser_driver_path = os.path.join('etc', 'chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
# options.add_argument("--headless")
service = Service(executable_path=browser_driver_path)

driver = webdriver.Chrome(service=service, options=options)

data_path = './data'
if os.path.isdir(data_path):
    shutil.rmtree(data_path)

os.makedirs(data_path)


def crawl_stock_price(company_code):
    driver.get(('https://finance.yahoo.com/quote/') + company_code +
               ('/history?period1=975110400&period2=1637798400&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true'))

    time.sleep(3)

    SCROLL_PAUSE_TIME = 0.5
    while True:
        try:
            # Scroll down to bottom
            driver.execute_script(
                'document.getElementsByClassName("Mstart(30px) Pt(10px)")[0].scrollIntoView({block: "end"})')

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

        except Exception as err:
            pass
            break

    time.sleep(3)

    web_content = BeautifulSoup(driver.page_source, features='lxml')
    rows = web_content.find_all('tr', {
        'class': 'BdT Bdc($seperatorColor) Ta(end) Fz(s) Whs(nw)'
    })

    data = []

    for i in range(len(rows)):
        record = rows[i].find_all('td')
        record = list(map(lambda cell: cell.text, record))
        record[0] = datetime.strptime(record[0], "%b %d, %Y")
        data.append(record)

    if len(data) > 0:
        header = ['Date', 'Open', 'High', 'Low',
                  'Close', 'Adj Close', 'Volume']
        df = pd.DataFrame(data)
        df.to_csv('./data/' + company_code + '.csv', sep=";", header=header)


COMPANY_CODE = ['^IXIC', 'PTN', 'SAVA']

for code in COMPANY_CODE:
    crawl_stock_price(code)


driver.close()
