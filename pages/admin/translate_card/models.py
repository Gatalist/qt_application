from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from components.browser import Browser
import time


class CardAttribute(QObject, Browser):
	send_result_translate = pyqtSignal(str)

	def __init__(self):
		super().__init__()

	def for_element_in_table(self, page_name: str):
		result = 'test translate'
		# try:
		page = self.pages[page_name].content()
		table = page.locator("xpath=//table[@id='data-table']/tbody/tr/td[3]")

		print("table:", table)

		# 	for attr in table:
		# 		div = attr.find_element(by=By.CLASS_NAME, value='valueWrapper')
		# 		uk = ''
		# 		ru = ''
		# 		md = ''
		# 		for a in div.find_elements(by=By.CSS_SELECTOR, value='a'):
		# 			if a.get_attribute('data-name') == 'ru':
		# 				ru = a
		# 				result = f"Name ru: {a.text}\n"
		# 			if a.get_attribute('data-name') == 'uk':
		# 				uk = a
		# 			if a.get_attribute('data-name') == 'md':
		# 				md = a
		# 		if uk.text == 'Пусто':
		# 			div_t = attr.find_element(by=By.CLASS_NAME, value='googleTranslateWrapper')
		# 			a_t = div_t.find_element(by=By.CSS_SELECTOR, value='a')
		# 			a_t.click()
		# 			time.sleep(1)
		#
		# 			yield result
		#
		# except StaleElementReferenceException:
		# 	pass

	def start(self, start_page, page_checking, item_in_page, link_translate):
		page_name = "citrus"
		self.create_page(page_name=page_name)
		self.login(page_name=page_name)
		self.open_url(page_name=page_name, link=link_translate)
		self.change_url(page_name=page_name, start_page=start_page, item_in_page=item_in_page)

		for page in range(1, int(page_checking) + 1):
			# print(page)
			# self.centre_browser()
			data_table = self.for_element_in_table(page_name=page_name)
			# for result in data_table:
			# 	if result:
			# 		print(result)
			# 		self.send_result_translate.emit(result)
			#
			# if page < int(page_checking):
			# 	new_page = self.next_url_translate(item_in_page)
			# 	self.open_url(new_page)
			# else:
			# 	self.open_url(self.web_browser.current_url)

		info_page_end = f"[+] Все атрибуты переведены\n"
		print(info_page_end)
		self.send_result_translate.emit(info_page_end)
				