from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from components.browser import Browser
import time
import re
import pyperclip


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

		# Определяем имя текстовой колонки для использования в модалке
		text_column_name = None
		for col in column_names:
			if col == 'name' or col == 'text_value':
				text_column_name = col
				break

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
							else:
								self.custom_translate(obj_page, row_data, link, text_column_name)

			if not row_data["translate"]:
				yield row_data
			else:
				yield {}

	@staticmethod
	def admin_translate(row_data, column_names, link, cells, pattern_uk):
		link.click()
		name_td = cells.nth(column_names.index("name"))

		# Ждем появления текста, но не падаем с ошибкой, если он уже там или не появился
		try:
			# Вместо wait_for используем ожидание с проверкой
			found = False
			for _ in range(20): # 10 секунд (20 * 0.5)
				if "uk: Есть перевод(" in name_td.inner_text():
					found = True
					break
				time.sleep(0.5)

			if not found:
				print("Текст 'Есть перевод' не появился вовремя")
		except Exception as e:
			print(f"Ошибка при ожидании перевода: {e}")

		# Теперь можно читать текст заново
		divs = name_td.locator("div")
		for k in range(divs.count()):
			div_text = divs.nth(k).inner_text().strip()
			if _match_uk := re.search(pattern_uk, div_text):
				row_data["uk"] = _match_uk.group(1)
		return row_data

	def google_page_translate(self, text: str):
		obj_page = self.pages[self.translate]
		obj_page.bring_to_front()
		self.open_url(page_name=self.translate, link=self.google_translate_page, wait_until="domcontentloaded")
		textarea = obj_page.locator('textarea[aria-label="Исходный текст"]')

		# 1. Кликаем, чтобы сфокусироваться
		textarea.click()
		textarea.fill(text)
		obj_page.wait_for_timeout(2000)
		copy_button = obj_page.locator('button[aria-label="Копировать перевод"]')

		try:
			copy_button.wait_for(state="visible", timeout=10000)  # Даем 10 секунд на перевод
			copy_button.click()
		except Exception as e:
			print(f"Кнопка копирования не появилась. Возможно, перевод не завершен: {e}")

		obj_page.wait_for_timeout(250)
		translated_text = pyperclip.paste()
		obj_page.locator('textarea[aria-label="Удалить исходный текст"]')

		return translated_text

	def custom_translate(self, obj_page, row_data, link, text_column_name="name"):
		# 1. Кликаем
		link.click()

		# Ждем сначала саму модалку (по классу или ID), а потом уже вкладку
		try:
			# Увеличиваем таймаут до 5 секунд и ждем именно видимости
			obj_page.wait_for_selector(".modal.in", state="visible", timeout=5000)
			# Теперь ждем активную вкладку
			obj_page.wait_for_selector(".tab-pane.active", state="visible", timeout=5000)
		except Exception as e:
			print(f"Ошибка: Модалка не открылась или вкладка не видна: {e}")
			# Если модалка не открылась, пробуем закрыть её (на всякий случай) и идем дальше
			obj_page.keyboard.press("Escape")
			return row_data

		active_pane = obj_page.locator(".tab-pane.active")

		# Используем динамическое имя колонки для поиска инпутов
		input_ru = active_pane.locator(f'input[name="{text_column_name}[ru]"]')
		input_uk = active_pane.locator(f'input[name="{text_column_name}[uk]"]')

		val_ru = input_ru.input_value()
		print(f"[RU] исходное значение: '{val_ru}'")
		if val_ru:
			# Попробуем сначала сфокусироваться
			input_uk.focus()
			input_uk.click()
			# translate_uk = val_ru
			if self.translate == "google_page":
				translate_uk = self.google_page_translate(text=val_ru)
				obj_page.bring_to_front()
			else:
				translate_uk = self.method_translate.translate_text(text=val_ru)

			# Заполняем UK
			input_uk.fill(translate_uk)
			row_data["uk"] = translate_uk

		else:
			print(f"[RU] пустое")

		# Ищем кнопку именно внутри открытой модалки
		save_button = obj_page.locator(".modal.in .modal-footer .btn-primary")

		# Проверяем, что кнопка есть и нажимаем
		if save_button.count() > 0:
			save_button.click()
			print("Кнопка 'Сохранить' нажата")

			obj_page.wait_for_selector(".modal-translations", state="hidden", timeout=10000)
			print("Модалка закрылась")
		else:
			print("Ошибка: Кнопка 'Сохранить' не найдена!")

		return row_data

	@staticmethod
	def validate_text_units(text):
		units = (
			'мм', 'см', 'м', 'км',
			'г', 'кг',
			'л', 'мл',
			'HZ',
		)
		return text.strip().lower().endswith(units)

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
		print("options:", result)
		return result

	def _select_option(self, page_name: str, option_name: str):
		obj_page = self.pages[page_name]
		select_locator = obj_page.locator("select#model_name")

		print(f"Выбираем опцию: {option_name}")
		select_locator.wait_for(state="visible")
		select_locator.select_option(label=option_name)

		# Ждём завершения сетевой активности (AJAX/Reload)
		obj_page.wait_for_timeout(2500)

		# Ждем, чтобы строки таблицы были прикреплены к DOM и видны
		try:
			obj_page.wait_for_selector("#data-table tbody tr", state="visible", timeout=5000)
			print("Таблица готова к работе")
		except Exception as e:
			print(f"Таблица не появилась или пуста: {e}")

	def start(self, page_name: str, start_page: int, checking_page: int, item_in_page, name_option):
		if start_page in [0, 1]:
			start_page = 0
		self.login(page_name=page_name)
		self.open_url(page_name=page_name, link=self.link_all_translate, wait_until="domcontentloaded")
		new_url = self.change_url(url=self.link_all_translate, start_page=start_page, item_in_page=item_in_page)
		self.open_url(page_name=page_name, link=new_url, wait_until="domcontentloaded")
		self._get_model_names(page_name=page_name)
		self._select_option(page_name=page_name, option_name=name_option)

		for page in range(start_page, checking_page - 1):
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

			time.sleep(2)

		info_page_end = f"[+] Все атрибуты переведены\n"
		print(info_page_end)
