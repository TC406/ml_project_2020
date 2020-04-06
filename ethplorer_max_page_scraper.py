from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from pathlib import Path
import json
import datetime
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

chrome_options = webdriver.ChromeOptions()
chrome_options.add_extension('ublock-origin_1_24_4_0.crx')
driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver',
                          chrome_options=chrome_options)
# time.sleep(30)
# driver = webdriver.Firefox()
contract_hashes = pd.read_csv("erc20_contracts_pandas.txt")
items_per_page = 100
start_page = 1725
max_page = 18258

max_page_list = []

for index, row in contract_hashes.iterrows():
    success_load_page_status = False
    first_try_page_fail = False
    while not success_load_page_status:
        if first_try_page_fail:
            driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver',
                                      chrome_options=chrome_options)
        now = datetime.datetime.now()
        page_address = ("https://ethplorer.io/address/" + row["contract_hash"]
                        + "#tab=tab-transfers&pageSize="
                        + str(items_per_page) + "&transfers=2")
        request = page_address
            # driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
        driver.get(request)
        driver.refresh()
        timeout = 5

        try:
            myElem = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID,'col-12 tab-content')))
            print
            "Page is ready!"
        except TimeoutException:
            print
            "Loading took too much time!"

        soup = BeautifulSoup(driver.page_source)
        try:
            max_page_list.append(int(soup.find("tr",class_="paginationFooter even last").find_all("a","page-link")[-1].text))
            print(index, row["token_name"], row["contract_hash"], max_page_list[-1])
            success_load_page_status = True
        except:
            first_try_page_fail = False
            print("ERROR", index,row["token_name"],row["contract_hash"],max_page_list[-1])

contract_hashes["max_page_number"] = max_page_list
contract_hashes.to_csv("erc20_contracts_with_max_page.csv")