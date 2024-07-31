from libs.citrus_api import CitrusApi
from libs.speed_test_api import SpeedPageTest
from libs.open_py_xl import CreateTable, Document
import time


# ------------------------ Полчучаем данные с Citrus Api
# получаем все данные всех товаров на странице / для сохранения задайте name_save
ctrs = CitrusApi()

open_file_url = open("open_url.txt", "r")
line_url = open_file_url.readlines()

new_file = open_file_url = open("idd.txt", "w")

for url in line_url:
    data = ctrs.parse_card(url=url)
    new_file.writelines(data)
    time.sleep(0.7)


new_file.close()

