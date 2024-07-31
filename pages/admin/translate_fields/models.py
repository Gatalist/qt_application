from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

import time
from components.browser import Base



class ProductGroupValue(QObject, Base):
	send_result_translate = pyqtSignal(str)

	def __init__(self):
		super().__init__()

	def for_element_in_table(self):
		result = ''
		try:
			table = self.web_browser.find_element(by=By.TAG_NAME, value="table")
			tbody = table.find_element(by=By.TAG_NAME, value='tbody')
			tr = tbody.find_elements(by=By.TAG_NAME, value='tr')
			for element in tr:
				columns_in_row = element.find_elements(by=By.TAG_NAME, value='td')
				column = 1
				name = 2
				translate = len(columns_in_row)

				uk_translate = ''
				ru_translate = ''

				for elem in columns_in_row:
					if column == name:
						for div in elem.find_elements(by=By.TAG_NAME, value='div'):
							if (div.text).startswith('uk:'):
								uk = div.find_element(by=By.TAG_NAME, value='a')
								uk_translate = uk.get_attribute('title')
							if (div.text).startswith('ru: '):
								ru = div.find_element(by=By.TAG_NAME, value='a')
								ru_translate = ru.get_attribute('title')

					if column == translate:
						if uk_translate == '':
							result += f"IDD: {columns_in_row[0].text}\n"
							result += f"--------------\n"
							result += f"Name ru: {ru_translate}\n"
							result += "Name uk: Translate..\n\n"

							for a in elem.find_elements(by=By.TAG_NAME, value='a'):
								if a.get_attribute('title') == 'google перевод':
									a.click()
									time.sleep(1)
					column += 1
				
				yield result
		
		except StaleElementReferenceException:
			pass


	def start(self, start_page, page_checking, item_in_page, link_translate, name_option):
		self.login()
		self.open_url(link_translate)
		self.search_model()
		self.select_options(name_option)
		self.change_url(start_page, item_in_page)

		for page in range(1, int(page_checking) + 1):
			info_page_start = f"\tCтраница: {page}\n"
			print(info_page_start)
			self.send_result_translate.emit(info_page_start)
			
			self.centre_browser()
			data_table = self.for_element_in_table()
			for result in data_table:
				if result:
					print(result)
					self.send_result_translate.emit(result)
			
			if page < int(page_checking):
				new_page = self.next_url_translate(item_in_page)
				self.open_url(new_page)
			else:
				self.open_url(self.web_browser.current_url)

		info_page_end = f"[+] Все атрибуты переведены\n"
		print(info_page_end)
		self.send_result_translate.emit(info_page_end)
