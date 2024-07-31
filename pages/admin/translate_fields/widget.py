from PyQt5.QtWidgets import QWidget
import threading

from .UI_window import Ui_Form
from .models import ProductGroupValue


class WindowTranslate(QWidget):
    def __init__(self):
        super(WindowTranslate, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.start_page = None
        self.end_page = None
        self.item_in_page = None
        self.url_translate = 'https://my.ctrs.com.ua/contento/translations/fields?search=&start=0&length=10&order=0&sort=asc'

        # привязываем события | чтение документа
        self.ui.open_browser.clicked.connect(self.open_browser)
        self.add_option_name()


    def open_browser(self):
        self.start_page = self.ui.start_page_text.text()
        self.end_page = self.ui.end_page_text.text()
        self.item_in_page = self.ui.item_page_text.text()
        name_option = self.ui.comboBox_option.currentText()

        # все атрибуты - перевод (товар - група значение свойство)
        self.model_translate = ProductGroupValue()

        threading.Thread(
            target = self.model_translate.start, 
            args=(self.start_page, self.end_page, self.item_in_page, self.url_translate, name_option)
            ).start()

        self.model_translate.send_result_translate.connect(self.view_result)

    def add_option_name(self):
        list_options = [
            "Товар: группы значений свойств",
            "Товар: группы свойств",
            "Товар: значение свойств",
            "Товар: значение свойств строка",
            "Товар: модификации",
            "Товар: свойства",
        ]

        self.ui.comboBox_option.clear() # очищаем список
        for option in list_options:
            self.ui.comboBox_option.addItem(option)

    def view_result(self, result):
        self.ui.textEdit.append(result)