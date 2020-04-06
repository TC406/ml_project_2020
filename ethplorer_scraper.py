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
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('csv_path', type=str,
                    help='an integer for the accumulator',
                    default='erc20_contracts_with_max_page.csv')
args = parser.parse_args()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_extension('ublock-origin_1_24_4_0.crx')
driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver',
                          chrome_options=chrome_options)
# time.sleep(30)
# driver = webdriver.Firefox()
contract_hashes = pd.read_csv(args.csv_path)

items_per_page = 100
start_page = 1
max_page = 18258
logs = []
contract_hashes = contract_hashes.sort_values(by=["max_page_number"])
for index, row in contract_hashes.iterrows():
    max_page = row["max_page_number"]
    now = datetime.datetime.now()
    dir_name = "outputs/" + row["token_name"] + now.strftime("_%d_%H_%M_%S") + "/"
    Path(dir_name).mkdir(parents=True, exist_ok=True)
    # Dumping parameters
    page_address = ("https://ethplorer.io/address/" + row["contract_hash"]
                    + "#tab=tab-transfers&pageSize="
                    + str(items_per_page) + "&transfers=")

    with open(dir_name + '/parameters.json', 'w') as f:
        json.dump({"items_per_page": items_per_page,
                   "token_name": row["token_name"],
                   "contract_hash": row["contract_hash"],
                   "time": datetime.datetime.now().replace(microsecond=0).isoformat(),
                   "url": page_address,
                   "max_page": max_page}, f)
    for page_number in range(start_page, max_page-1):
        success_load_page_status = False
        first_try_page_fail = False
        while not success_load_page_status:
            request = page_address + str(page_number)
            # driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
            if first_try_page_fail:
                driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver',
                                          chrome_options=chrome_options)
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
                full_page_table_even = soup.find("div",class_="col-12 tab-content").find_all("tr",class_="even")
                full_page_table_odd = soup.find("div",class_="col-12 tab-content").find_all("tr",class_="odd")
                full_page_table = full_page_table_even + full_page_table_odd

                test_load = int(soup.find("tr",class_="paginationFooter even last").find_all("a","page-link")[-1].text)
                success_load_page_status = True
            except:
                first_try_page_fail = False
                print("ERROR",index,row["token_name"],row["contract_hash"])
                continue

            transfers_qty_values = []
            tx_list = []
            from_list = []
            to_list = []
            timestamp_data = []
            value_in_usd = []
            # some_percents = []
            for count, table_item in enumerate(full_page_table):
                try:
                    buf_local_link = table_item.findAll("a", "local-link")
                    if len(buf_local_link) == 0:
                        continue
                    timestamp_data.append(buf_local_link[0].text)
                    tx_list.append(buf_local_link[1].text)
                    from_list.append(buf_local_link[2].text)
                    to_list.append(buf_local_link[3].text)
                    transfers_qty_values.append(float(table_item.find("div",
                                                                      "transfers-qty-value").text.split()[0].replace(",", "")))
                    # date_timestamp = datetime.datetime.strptime(buf_local_link[0].text, '%Y-%m-%d %H:%M:%S')
                    # transfer_string_buf = table_item.find("span", "transfer-usd").text.replace(",", "").replace("$\xa0", "").split(
                    #     "(")
                    # value_in_usd.append(float(transfer_string_buf[0]))
                except:
                    print("Non-sucesfull item_retrivial")
                    continue
                # some_percents.append(float(transfer_string_buf[1].split("%")[0]))
            #     print(count)

            columns = ["timestamp", "token_qty_values", "tx_address", "from_address",
                       "to_address"]
            values = [timestamp_data, transfers_qty_values, tx_list, from_list, to_list]
            dataframe_page = pd.DataFrame(values)
            dataframe_page = dataframe_page.transpose()
            dataframe_page.columns = columns
            # pd.DataFrame(values, columns=columns)
            dataframe_page.to_csv(dir_name + "_" + str(page_number) + ".csv")
            print(row["token_name"], page_number, dataframe_page.shape[0], timestamp_data[-1])
        current_date = datetime.datetime.strptime(timestamp_data[-1], '%Y-%m-%d %H:%M:%S')
        if current_date < datetime.datetime(2018, 1, 1, 0, 0, 0):
            break




#
# request = "https://ethplorer.io/address/0xb63b606ac810a52cca15e44bb630fd42d8d1d83d?from=search#tab=tab-transfers&transfers=16&pageSize=100"
# driver.get(request)
# soup = BeautifulSoup(driver.page_source)
#
# full_page_table_even = soup.find("div", class_="col-12 tab-content").find_all("tr", class_="even")
# full_page_table_odd = soup.find("div", class_="col-12 tab-content").find_all("tr", class_="odd")
#
# len(full_page_table_even)
# len(full_page_table_odd)
#
# full_page_table = full_page_table_even + full_page_table_odd
# len(full_page_table)
#
#
# transfers_qty_values = []
# tx_list = []
# from_list = []
# to_list = []
# timestamp_data = []
# value_in_usd = []
# some_percents = []
# for count, table_item in enumerate(full_page_table):
#     buf_local_link = table_item.findAll("a", "local-link")
#     if len(buf_local_link) == 0:
#         continue
#     timestamp_data.append(buf_local_link[0].text)
#     tx_list.append(buf_local_link[1].text)
#     from_list.append(buf_local_link[2].text)
#     to_list.append(buf_local_link[3].text)
#     transfers_qty_values.append(float(table_item.find("div",
#                                                       "transfers-qty-value").text.split()[0].replace(",", "")))
#     transfer_string_buf = table_item.find("span", "transfer-usd").text.replace(",", "").replace("$\xa0", "").split("(")
#     value_in_usd.append(float(transfer_string_buf[0]))
#     some_percents.append(float(transfer_string_buf[1].split("%")[0]))
# #     print(count)
#
#
# columns = ["timestamp", "token_qty_values", "tx_address", "from_address",
#            "to_address", "value_in_usd", "some_percents"]
# values = np.array([timestamp_data, transfers_qty_values, tx_list, from_list, to_list,
#          value_in_usd, some_percents])
#
#
# dataframe_page = pd.DataFrame(values.T, columns=columns)
#
# dataframe_page.to_csv()
#
#
# transfer_string_buf = table_item.find("span", "transfer-usd").text.replace(",", "").replace("$\xa0", "").split("(")
#
#
# float(transfer_string_buf[0])
#
#
# float(transfer_string_buf[1].split("%")[0])
#
#
# # In[62]:
#
#
# transfers_qty_values
#
#
# # In[83]:
#
#
# len(tx_list)

