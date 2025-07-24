from playwright.sync_api import sync_playwright
import json
import os
import re
import time
from settings import Settings


class Browser:
    def __init__(self, visible=False):
        self.current_directory = os.getcwd()
        self.cookie_file = os.path.join(Settings.ROOT_PATH, "components", "session.json")
        self.visible = visible
        self.base_url_admin = 'https://my.ctrs.com.ua'
        self.link_login = self.base_url_admin + '/ru/auth/login'
        self.link_login_email = self.base_url_admin + '/ru/auth/email'
        self.link_login_sms = self.base_url_admin + '/ru/auth/sms_code'

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

    def open_url(self, page_name: str, link: str, wait_until="load"):
        return self.pages[page_name].goto(link, wait_until=wait_until)

    # def change_url(self, page_name: str, start_page: int, item_in_page: int):
    #     current_url = self.pages[page_name].url
    #     current_url = re.sub(r'start=\d+', f'start={start_page}', current_url)
    #     current_url = re.sub(r'length=\d+', f'length={item_in_page}', current_url)
    #     self.open_url(page_name=page_name, link=current_url)

    # def next_url_translate(self, item_in_page: int):
    #     current_url = self.pages[page_name].url
    #     match = re.search(r'start=(\d+)', current_url)
    #     if match:
    #         new_start = int(match.group(1)) + int(item_in_page)
    #         current_url = re.sub(r'start=\d+', f'start={new_start}', current_url)
    #     return current_url

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

    @staticmethod
    def get_json_for_pre(content):
        match = re.search(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                print("✅ Успешно загружено", len(data), "записей")
                # print("data:", data)
                return data
            except json.JSONDecodeError as e:
                print("❌ Ошибка парсинга JSON:", e)
                return []
        else:
            print("❌ JSON не найден в <pre>...")
