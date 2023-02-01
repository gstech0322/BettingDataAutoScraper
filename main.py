from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import yaml
from selenium import webdriver
from lxml import html
from pprint import pprint
import pandas as pd
import time
from datetime import datetime
import sys
import os
import re


def _driver():
    s = Service(ChromeDriverManager().install())

    user = "USER_1"

    dirr = os.path.abspath(os.curdir).rsplit("\\", 1)[0] + f"\\{user}"

    options = Options()
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features")
    # options.add_argument("-headless")
    options.add_argument("excludeSwitches")
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument(
        r"user-data-dir=%s" % dirr)

    driver = webdriver.Chrome(service=s, options=options)
    driver.maximize_window()
    driver.implicitly_wait(5)

    return driver


filename = "data.csv"

def prettir(txt):
    try:
        txt = re.sub(r"[\r\t]", " ", str(txt))
        txt = re.sub(r"[\n]", " ", str(txt))
        txt = ' '.join(txt.split())
    except IndexError:
        txt = txt
    return txt


def save_to_file(df, keep):
    if keep == True:
        try:
            pd.read_csv(filename)
            df.to_csv(filename, index=False, mode="a",
                    header=False, encoding='utf-8-sig')
        except FileNotFoundError:
            df.to_csv(filename, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(filename, index=False, encoding='utf-8-sig')

def json_convert(df):
    df = df.drop_duplicates()
    df = df.to_json("data.json", orient='records')

def login():
    time.sleep(2.5)
    try:
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
    except:
        pass
    try:
        username = find(By.XPATH, '//input[@name="UserName"]')
        username.send_keys("A6050")
        password = find(By.XPATH, '//input[@name="Password"]')
        password.send_keys("123" + "\n")
        time.sleep(3)
        print("login successful")
    except:
        pass


def _idx(x):
    try:
        return x[0]
    except IndexError:
        return None


def get_data(row, keep):
    print("row:::")
    print(row)
    os.system('color')
    ticket = row.xpath('.//td[@data-title="TRANSACTION:"]/text()')
    print("ticket::")
    print(ticket)
    if ticket:
        date_placed = " ".join(row.xpath('.//td[@data-title="DATE PLACED:"]/text()'))
        wager_type= _idx(row.xpath('.//td[@data-title="DESCRIPTION:"]/span[1]/text()'))
        game_date = _idx(row.xpath('.//td[@data-title="DESCRIPTION:"]/span[2]/text()'))
        wd = prettir(" ".join([x for x in row.xpath('.//td[@data-title="DESCRIPTION:"]/text()') if x]))
        if wd:
            sport = wd.rsplit(" - ", 1)[-1].strip()
            description = wd.rsplit(" - ", 1)[0].strip()
        else:
            sport = None
            description = None
        status = row.xpath('.//td[@data-title="STATUS:"]/text()')
        cashout = row.xpath('.//td[@data-title="CASHOUT:"]/text()')
        risk_win = row.xpath('.//td[@data-title="RISK/WIN:"]/span/text()')
        total = row.xpath('//tr/td[@class="font-weight-bold border-0 text-center"]/text()')

        p = {
            "DATE PLACED": prettir(date_placed),
            "Scraped Date": datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
            "TICKET#": prettir(_idx(ticket)),
            "WAGER TYPE": wager_type,
            "GAME DATE": game_date,
            "SPORT": sport,
            "DESCRIPTION": description,
            "STATUS": prettir(_idx(status)),
            "CASHOUT": prettir(_idx(cashout)),
            "RISK/WIN":prettir(_idx(risk_win)),
            "TOTAL": prettir(_idx(total))
        }

        print("\033[92m")
        pprint(p)
        print("\033[0m")
        df = pd.DataFrame([p])
        save_to_file(df, keep)
   


def Scraper(link):
    global driver, find, finds
    driver = _driver()
    find = driver.find_element
    finds = driver.find_elements
    driver.get(link)
    driver.implicitly_wait(10)
    login()
    open_bets = find(By.XPATH, '//li/a[@class="nav-link sub-menu-link2"][text() ="OPEN BETS"]')
    open_bets.click()
    time.sleep(2)
    keep = False
    while True:
        tree = html.fromstring(html=driver.page_source)
        xpath = '//tbody[@class="open-betsbody rounded"]/tr[@class="border-0 selected-row" or @class="border-0"]'
        rows =tree.xpath(xpath)
        for row in rows:
            get_data(row, keep)
            keep = True
        keep = False
        time.sleep(15)
        driver.refresh()

Scraper("https://1bettor.com/Common/Dashboard")