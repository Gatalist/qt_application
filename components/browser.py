from selenium import webdriver
from selenium.webdriver.common.by import By
import pickle
import time
import re
import os
from settings import Settings



class Browser():
    def __init__(self):
        self.current_directory = os.getcwd()
        self.cookie_file = Settings.COOKIES
        print(self.cookie_file)
        self.web_browser = webdriver.Chrome()
        self.base_url_admin = 'https://my.ctrs.com.ua'
        self.link_login = self.base_url_admin + '/ru/auth/login'
        self.link_login_email = self.base_url_admin + '/ru/auth/email'
        self.link_login_sms = self.base_url_admin + '/ru/auth/sms_code'

    # открытие ссылок
    def open_url(self, link):
        # print(link)
        self.web_browser.get(link)
        time.sleep(2)

    # изменение ссылки
    def change_url(self, start_page, item_in_page):
        current_url = self.web_browser.current_url
        start = re.search(r'start=(\d+)', current_url)
        length = re.search(r'length=(\d+)', current_url)
        
        txt_start = start.group()
        txt_length = length.group()

        current_url.replace(txt_start, f'start={start_page}')
        current_url.replace(txt_length, f'length={item_in_page}')
        
        new_url = current_url.replace(
            txt_start, f'start={start_page}'
        ).replace(
            txt_length, f'length={item_in_page}'
        )

        self.open_url(new_url)

    # генерация следующей ссылки
    def next_url_translate(self, item_in_page):
        current_url = self.web_browser.current_url
        
        start = re.search(r'start=(\d+)', current_url)
        
        txt_start = start.group()

        new_number = int(start.group(1)) + int(item_in_page)

        new_url = current_url.replace(txt_start, f'start={new_number}')
        return new_url

    # первая авторизация / сохраняем cookies
    def auth_user(self):
        self.open_url(self.link_login)
        print('Авторизация пользователя')
        while True:
            if self.link_login == self.web_browser.current_url or \
                    self.link_login_email == self.web_browser.current_url or \
                    self.link_login_sms == self.web_browser.current_url:
                time.sleep(3)
                print('more..')
            else:
                time.sleep(5)
                break
        pickle.dump(self.web_browser.get_cookies(), open(self.cookie_file, 'wb'))

    # авторизация / по сохраненным cookies
    def get_cookie_user(self):
        self.open_url(self.link_login)
        print(self.cookie_file, 'read')
        for cookie in pickle.load(open(self.cookie_file, 'rb')):
            self.web_browser.add_cookie(cookie)

    def login(self):
        try:
            self.get_cookie_user()
            print("Куки загружены")
        except FileNotFoundError:
            self.auth_user()
            print('Вы вошли в систему! Данные сохранены')


class Base(Browser):
    def __init__(self):
        super().__init__()
        self.options = "//select[@id='model_name']/option"  # выбор модели для перевода
        self.table_name = "//table[@id='data-table']/tbody/tr/td[2]"
        self.modal = "//div[@id='name']/div"
        self.table_filter = "//div[@id='data-table_filter']"
        self.list_options = []
    
    def get_all_options(self):
        return self.web_browser.find_elements(by=By.XPATH, value=self.options)
    
    def search_model(self):
        # Найдем все элементы option внутри select
        options = self.web_browser.find_elements(by=By.XPATH, value=self.options)
        for option in options:
            print("[",  option.text, "]")
            if option.text.startswith("Товар: "):
                self.list_options.append(option.text)
        # self.send_list_options_name.emit(self.list_options)

    def select_options(self, name):
        # Найдем элемент select
        select = self.web_browser.find_elements(by=By.XPATH, value=self.options)
        # Найдем все элементы option внутри select
        for option_click in select:
            if option_click.text == name:
                option_click.click()
                time.sleep(2)

    def centre_browser(self):
        self.web_browser.find_element(by=By.XPATH, value=self.table_filter).location_once_scrolled_into_view
        time.sleep(1)
