from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from components.browser import Browser
from playwright.sync_api import TimeoutError
import time
import re


class ProductGroupValue(QObject, Browser):
	send_result_translate = pyqtSignal(str)

	def __init__(self, queue, translate, visible=False):
		super().__init__(visible=visible, translate=translate)
		self.queue = queue
		self.translate = translate

	def for_element_in_table(self, page_name: str):
		obj_page = self.pages[page_name]
		headers = obj_page.locator("table thead tr th")
		print("headers:", headers.count())
		column_names = [headers.nth(i).inner_text() for i in range(headers.count())]
		print("Колонки:", column_names)

		rows = obj_page.locator("#data-table tbody tr")
		row_count = rows.count()
		print("Найдено строк:", row_count)

		pattern_ru = r"ru: Есть перевод\((.*?)\)"
		pattern_uk = r"uk: Есть перевод\((.*?)\)"

		for i in range(row_count):
			row = rows.nth(i)
			cells = row.locator("td")

			row_data = {
				"translate": True
			}

			for j in range(cells.count()):

				if column_names[j] == 'ID':
					td = cells.nth(j)
					row_data["id"] = td.inner_text()

				if column_names[j] == 'name' or column_names[j] == 'text_value': # колонка с переводами (текст)
					td = cells.nth(j)
					divs = td.locator("div")

					for k in range(divs.count()):
						div_text = divs.nth(k).inner_text().strip()

						if div_text == "uk: Нет перевода()":
							row_data["translate"] = False
							row_data["uk"] = ""

						if _match_uk := re.search(pattern_uk, div_text):
							row_data["uk"] = _match_uk.group(1)

						if _match_ru := re.search(pattern_ru, div_text):
							row_data["ru"] = _match_ru.group(1)

				if column_names[j] == '':  # btn translate
					if not row_data["translate"]:
						td = cells.nth(j)
						links = td.locator("a")

						for k in range(links.count()):
							link = links.nth(k)

							# кнопка перевода с админки
							if link.get_attribute("title") and self.translate == "admin":
								self.admin_translate(row_data, column_names, link, cells, pattern_uk)

							elif self.translate == "deepl":
								self.deepl_translate()

			time.sleep(1)

			if not row_data["translate"]:
				yield row_data
			else:
				yield {}

	@staticmethod
	def admin_translate(row_data, column_names, link, cells, pattern_uk):
		link.click()

		# Ждём появления div с нужным текстом внутри ячейки name
		name_td = cells.nth(column_names.index("name"))
		try:
			name_td.locator("div", has_text="uk: Есть перевод(").wait_for(timeout=10000)
		except TimeoutError:
			print("Превышено время ожидания появления текста 'uk: Есть перевод('")
		# Можно добавить retry или пропустить этот элемент

		# Теперь можно читать текст заново
		divs = name_td.locator("div")
		for k in range(divs.count()):
			div_text = divs.nth(k).inner_text().strip()
			if _match_uk := re.search(pattern_uk, div_text):
				row_data["uk"] = _match_uk.group(1)
		return row_data

	@staticmethod
	def deepl_translate():
		print("deepl_translate")

	def _get_model_names(self, page_name):
		obj_page = self.pages[page_name]
		# Ждём появления хотя бы одной строки таблицы
		obj_page.wait_for_selector("#data-table tbody tr")
		selects = obj_page.locator("select#model_name option")

		result = []
		for i in range(selects.count()):
			select = selects.nth(i)
			# k_v = select.get_attribute("value"), select.inner_text()
			result.append(select.inner_text())
		return result

	def _select_option(self, page_name: str, option_name: str):
		obj_page = self.pages[page_name]
		# Ждём появления хотя бы одной строки таблицы
		obj_page.locator("select#model_name").select_option(
			label=option_name
		)
		obj_page.wait_for_selector("#data-table tbody tr")

	def start(self, page_name: str, start_page: int, checking_page: int, item_in_page, link_translate, name_option):
		self.login(page_name=page_name)
		self.open_url(page_name=page_name, link=link_translate, wait_until="domcontentloaded")
		new_url = self.change_url(url=link_translate, start_page=start_page, item_in_page=item_in_page)
		self.open_url(page_name=page_name, link=new_url, wait_until="domcontentloaded")
		self._get_model_names(page_name=page_name)
		self._select_option(page_name=page_name, option_name=name_option)

		for page in range(int(checking_page) + 1):
			info_page_start = f"\tCтраница: {page}\n"
			print(info_page_start)

			data_table = self.for_element_in_table(page_name=page_name)
			for result in data_table:
				if result:
					self.queue.put(result)

			if page <= int(checking_page):
				new_page = self.next_url_translate(page_name=page_name, next_items=item_in_page)
				print("next_url:", new_page)
				self.open_url(page_name=page_name, link=new_page, wait_until="domcontentloaded")

		info_page_end = f"[+] Все атрибуты переведены\n"
		print(info_page_end)

