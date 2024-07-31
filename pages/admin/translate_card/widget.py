from PyQt5.QtWidgets import QWidget
import threading

from .UI_window import Ui_Form
from .models import CardAttribute


class WindowTranslateCard(QWidget):
    def __init__(self):
        super(WindowTranslateCard, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.start_page = None
        self.end_page = None
        self.item_in_page = None

        # привязываем события | чтение документа
        self.ui.open_browser.clicked.connect(self.open_browser)

    def open_browser(self):
        self.start_page = self.ui.start_page_text.text()
        self.end_page = self.ui.end_page_text.text()
        self.item_in_page = self.ui.item_page_text.text()
        self.translate_url = self.ui.translate_url_text.text()

        # перевод атрибутов в карточке товара
        self.model_translate = CardAttribute()

        threading.Thread(
            target = self.model_translate.start, 
            args=(self.start_page, self.end_page, self.item_in_page, self.translate_url)
            ).start()

        self.model_translate.send_result_translate.connect(self.view_result)

    def view_result(self, result):
        self.ui.textEdit.append(result)