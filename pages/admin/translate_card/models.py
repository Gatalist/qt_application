from time import sleep
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from components.browser import Browser


class CardAttribute(QObject, Browser):
	send_result_translate = pyqtSignal(str)

	def __init__(self, queue, visible=False):
		super().__init__(visible=visible)
		self.queue = queue

	def for_element_in_table(self, page_name: str):
		obj_page = self.pages[page_name]

		# Ждём появления хотя бы одной строки таблицы
		obj_page.wait_for_selector("#data-table tbody tr")

		# Получаем заголовки один раз, так как они не меняются
		headers = obj_page.locator("table thead tr th")
		column_names = [headers.nth(i).inner_text() for i in range(headers.count())]
		print("Колонки:", column_names)

		# Ищем индексы нужных колонок
		id_col_index = column_names.index('ID')
		value_col_index = column_names.index('Значение')

		found_untranslated_row = True

		while found_untranslated_row:
			# Получаем строки таблицы заново на каждой итерации
			rows = obj_page.locator("#data-table tbody tr")
			row_count = rows.count()
			print("[ + ] Найдено строк:", row_count, "new while")

			check_count = 0

			for i in range(row_count):
				# Получаем ячейки текущей строки по индексу
				row_cells = rows.nth(i).locator("td")

				# Собираем данные строки. Обращаемся к ячейкам по их индексам.
				# Это исключает лишний цикл `for j in range(cells.count())`
				row_data = {
					"id": row_cells.nth(id_col_index).inner_text(),
					"translate": True
				}

				# Получаем локатор для ячейки "Значение"
				value_td = row_cells.nth(value_col_index)

				# Находим ссылки внутри ячейки "Значение"
				wrapper_links = value_td.locator("div.valueWrapper a")

				# Проверяем ссылки на наличие пустого украинского перевода
				# и получаем русский текст.
				uk_link_text = ""
				ru_link_text = ""
				for link_idx in range(wrapper_links.count()):
					link = wrapper_links.nth(link_idx)
					name = link.get_attribute("data-name")
					text = link.inner_text()

					if name == 'uk':
						uk_link_text = text
					if name == 'ru':
						ru_link_text = text

				row_data["ru"] = ru_link_text

				if uk_link_text == 'Пусто':
					print("link_text uk: Пусто")
					row_data["translate"] = False

					# Кликаем по кнопке перевода
					google_translate_btn = value_td.locator("div.googleTranslateWrapper a")
					google_translate_btn.click()

					yield {}
					sleep(1.5)
					break
				else:
					yield {}
					check_count += 1

				print("row_count:", row_count, "|", "check_count:", check_count)

			if check_count == row_count:
				print("Все строки переведены. Завершение работы.")
				yield {}
				found_untranslated_row = False

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
		new_url = self.change_url(url=link_translate, start_page=start_page, item_in_page=item_in_page)
		sleep(1)
		self.open_url(page_name=page_name, link=new_url, wait_until="domcontentloaded")

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

			sleep(1.5)

		info_page_end = f"[+] Все атрибуты переведены\n"
		print(info_page_end)
