from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from components.browser import Browser
import time


class CardAttribute(QObject, Browser):
	send_result_translate = pyqtSignal(str)

	def __init__(self, queue, visible=False):
		super().__init__(visible=visible)
		self.queue = queue

	def for_element_in_table(self, page_name: str):
		obj_page = self.pages[page_name]

		# Ждём появления хотя бы одной строки таблицы
		obj_page.wait_for_selector("#data-table tbody tr")

		headers = obj_page.locator("table thead tr th")
		print("headers:", headers.count())
		column_names = [headers.nth(i).inner_text() for i in range(headers.count())]
		print("Колонки:", column_names)

		obj_page.wait_for_selector("#data-table tbody tr")

		rows = obj_page.locator("#data-table tbody tr")
		row_count = rows.count()
		print("Найдено строк:", row_count)

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

				if column_names[j] == 'Значение':
					td = cells.nth(j)

					div_value_wrapper = td.locator("div.valueWrapper")
					wrapper_links = div_value_wrapper.locator("a")

					google_translate = td.locator("div.googleTranslateWrapper a")

					for k in range(wrapper_links.count()):
						link = wrapper_links.nth(k)
						name = link.get_attribute("data-name")
						link_text = link.inner_text()

						if name == 'uk' and link_text == 'Пусто':
							print("link_text uk:", link_text)
							row_data["translate"] = False

						if name == 'ru':
							print("link_text ru:", link_text)
							row_data["ru"] = link_text

					if not row_data["translate"]:
						google_translate.click()
						time.sleep(2)

						# Ждём, пока внутри td появится перевод
						obj_page.wait_for_function(
							"""(node) => {
                                const el = node.querySelector("div.valueWrapper a[data-name='uk']");
                                return el && el.innerText !== 'Пусто';
                            }""",
							arg=td.element_handle()
						)

						# Читаем обновлённые ссылки
						wrapper_links = td.locator("div.valueWrapper a")

						for e in range(wrapper_links.count()):
							_link = wrapper_links.nth(e)
							_name = _link.get_attribute("data-name")
							_link_text = _link.inner_text()

							if _name == 'uk':
								print("new_link_text uk:", _link_text)
								row_data["uk"] = _link_text

			print("row_data:", row_data)
			if not row_data["translate"]:
				yield row_data
			else:
				yield {}

	@staticmethod
	def wait_for_non_empty_text(locator, expected="Пусто", timeout=5000):
		locator.wait_for(timeout=timeout)
		locator.page.wait_for_function(
			"(el, expected) => el && el.innerText !== expected",
			arg=locator,
			arg1=expected,
			timeout=timeout
		)

	def start(self, page_name: str, start_page: int, checking_page: int, item_in_page: int, link_translate: str):
		self.login(page_name=page_name)
		self.open_url(page_name=page_name, link=link_translate, wait_until="domcontentloaded")
		self.change_url(page_name=page_name, start_page=start_page, item_in_page=item_in_page)

		for page in range(int(checking_page) + 1):
			info_page_start = f"\tCтраница: {page}\n"
			print(info_page_start)
			# self.send_result_translate.emit(info_page_start)

			# self.centre_browser()
			data_table = self.for_element_in_table(page_name=page_name)
			for result in data_table:
				if result:
					self.queue.put(result)
			# self.send_result_translate.emit(result)

			if page <= int(checking_page):
				new_page = self.next_url_translate(page_name=page_name, next_page=page)
				print("next_url:", new_page)
				self.open_url(page_name=page_name, link=new_page, wait_until="domcontentloaded")

		info_page_end = f"[+] Все атрибуты переведены\n"
		print(info_page_end)
		# self.send_result_translate.emit(info_page_end)
				