from libs.citrus_api import CitrusApi
from libs.speed_test_api import SpeedPageTest
from libs.open_py_xl import CreateTable, Document



category_url = 'smartfony'
content_type = '' #'.webp'
page_ctart = 1
page_end = 1
test_version_page = 'mobile' # mobile or desktop
file_name_save = 'smartfony'
open_json_to_speed_test = file_name_save + content_type + '.json'
save_name_result_test = 'ResultSpeedPageTest'
save_name_xl = file_name_save + content_type


# ------------------------ Полчучаем данные с Citrus Api
# получаем все данные всех товаров на странице / для сохранения задайте name_save
ctrs = CitrusApi()
data = ctrs.parse_category_card(category_url=category_url, page_ctart=page_ctart, page_end=page_end, name_save=None)

# ctrs = ctrs.get_galery_and_description_img(data, "data_card_desc_galery")

# # получаем нужные данные товаров на странице и сохраняем в файл
# ctrs.get_data_card(data=data, name_save=file_name_save, content_type=content_type)


# ------------------------ Полчучаем данные с Google Speed Page Test API
# получаем результаты с API SpeedPageTest и сохраняем в файл
# speed_page_test = SpeedPageTest()
# data_json = speed_page_test.worker(open_json=open_json_to_speed_test, test_version_page=test_version_page, save_name=save_name_result_test)  


# ------------------------ Записываем в xlsx документ
# pyxl = CreateTable(save_name_xl)
# # создаем лист на который будем записывать данные
# sheet_obj = pyxl.add_new_sheet('content - webp')
# # добавляем титульную строку
# pyxl.add_title_column(sheet_obj)
# # добавляем результаты Speed Page Test
# pyxl.complete_table(sheet_obj, save_name_result_test)
# # добавляем средние результаты в конец
# pyxl.complete_average_value(sheet_obj)
# # сохраняем файл
# pyxl.save_xlsx(save_name_xl)