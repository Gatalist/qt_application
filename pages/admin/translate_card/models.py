from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

import time
from components.browser import Base



class CardAttribute(QObject, Base):
	send_result_translate = pyqtSignal(str)

	def __init__(self):
		super().__init__()

	def for_element_in_table(self):
		result = 'test translate'
		try:
			table = self.web_browser.find_elements(by=By.XPATH, value="//table[@id='data-table']/tbody/tr/td[3]")
			for attr in table:
				div = attr.find_element(by=By.CLASS_NAME, value='valueWrapper')
				uk = ''
				ru = ''
				md = ''
				for a in div.find_elements(by=By.CSS_SELECTOR, value='a'):
					if a.get_attribute('data-name') == 'ru':
						ru = a
						result = f"Name ru: {a.text}\n"
					if a.get_attribute('data-name') == 'uk':
						uk = a
					if a.get_attribute('data-name') == 'md':
						md = a
				if uk.text == 'Пусто':
					div_t = attr.find_element(by=By.CLASS_NAME, value='googleTranslateWrapper')
					a_t = div_t.find_element(by=By.CSS_SELECTOR, value='a')
					a_t.click()
					time.sleep(1)

					yield result

		except StaleElementReferenceException:
			pass

	def start(self, start_page, page_checking, item_in_page, link_translate):
		self.login()
		self.open_url(link_translate)
		self.change_url(start_page, item_in_page)

		for page in range(1, int(page_checking) + 1):
			# print(page)
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
				