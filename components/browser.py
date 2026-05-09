from playwright.sync_api import sync_playwright
import json
import os
import re
import time
from settings import Settings
from components.deepl_api import DeepLTranslator


class Browser:
    def __init__(self, visible=False, translate="admin"):
        self.current_directory = os.getcwd()
        self.cookie_file = os.path.join(Settings.ROOT_PATH, "source", "session.json")
        self.api_key_file = os.path.join(Settings.ROOT_PATH, "source", "api_keys.json")
        self.visible = visible
        self.base_url_admin = 'https://my.ctrs.com.ua'
        self.link_login = self.base_url_admin + '/ru/auth/login'
        self.link_login_email = self.base_url_admin + '/ru/auth/email'
        self.link_login_sms = self.base_url_admin + '/ru/auth/sms_code'
        self.link_all_translate = self.base_url_admin + '/contento/translations/fields?search=&start=0&length=5&order=0&sort=asc'
        self.google_translate_page = "https://translate.google.com/?hl=ru&sl=ru&tl=uk&op=translate"
        self.translates = ["admin", "deepl", "google_page"]
        if translate not in self.translates:
            raise f"Not valid method '{translate}' translate"
        self.api_key = self.get_api_key(translate)
        # self.deepl_translate = DeepLTranslator(self.api_key)
        self.method_translate = self.get_method_translate(translate)
        self.headless = False if self.visible else True # visible Ui interface
        self.pages = {}

        self.playwright = None
        self.browser = None
        self.context = None

    def create_browser(self):
        if not self.playwright:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
            )
            self.context = self.browser.new_context(
                viewport=None
            )

    def create_page(self, page_name: str):
        self.create_browser()
        self.pages[page_name] = self.context.new_page()
        self.pages[page_name].set_viewport_size({"width": 1560, "height": 1460})

    def remove_page(self, page_name: str):
        del self.pages[page_name]

    def save_cookies(self):
        """ Сохранить куки """
        cookies = self.context.cookies()
        with open(self.cookie_file, "w") as f:
            json.dump(cookies, f)

    def get_cookies(self):
        """ загрузка cookies """
        with open(self.cookie_file, "r") as f:
            cookies = json.load(f)
            self.context.add_cookies(cookies)

    def get_api_key(self, name: str) -> str | None:
        try:
            with open(self.api_key_file, "r") as f:
                api_keys = json.load(f)
                for item in api_keys:
                    if item["name"] == name:
                        return item["value"]
                return None
        except FileNotFoundError:
            return None
    
    def get_method_translate(self, text: str) -> object | None:
        if text == "deepl":
            return self.deepl_translate
        elif text == "admin":
            return None
        elif text == "google_page":
            return None
        else:
            raise f"Not valid method '{self.method_translate}' translate"
        
    def open_url(self, page_name: str, link: str, wait_until="domcontentloaded"):
        print("[ + ] open_url:", link)
        self.pages[page_name].goto(link, wait_until=wait_until)
        self.pages[page_name].wait_for_load_state("networkidle", timeout=5000)
        return self.pages[page_name]

    @staticmethod
    def change_url(url: str, start_page: int, item_in_page: int):
        start_item = 0 if start_page == 0 else start_page * item_in_page
        replace_start = re.sub(r'start=\d+', f'start={start_item}', url)
        replace_length = re.sub(r'length=\d+', f'length={item_in_page}', replace_start)
        print("new_url:", replace_length)
        return replace_length

    def next_url_translate(self, page_name: str, next_items: int):
        current_url = self.pages[page_name].url
        match = re.search(r'start=(\d+)', current_url)
        if match:
            new_start = int(match.group(1)) + int(next_items)
            current_url = re.sub(r'start=\d+', f'start={new_start}', current_url)

        # Принудительно устанавливаем length, чтобы сервер не менял его на дефолтный
        current_url = re.sub(r'length=\d+', f'length={next_items}', current_url)
        return current_url

    def auth_user(self, page_name: str):
        self.open_url(page_name, self.link_login, wait_until="domcontentloaded")
        print('Авторизация пользователя...')
        while True:
            # current_url = self.pages[page_name].url
            current_url = self.pages[page_name].wait_for_url(re.compile(r'^(?!.*auth).*'), timeout=0)  # 0 — бесконечно ждёт, пока URL не выйдет за пределы auth/*
            print("current_url:", current_url)
            print([self.link_login, self.link_login_email, self.link_login_sms])
            if current_url in [self.link_login, self.link_login_email, self.link_login_sms]:
                time.sleep(3)
                print('Ожидание ввода...')
            else:
                time.sleep(5)
                break
        self.save_cookies()

    def login(self, page_name: str):
        try:
            self.get_cookies()
            print("Куки загружены")
        except FileNotFoundError:
            self.auth_user(page_name=page_name)
            print("Вы вошли в систему, данные сохранены")

    def close(self):
        self.browser.close()
        self.playwright.stop()
