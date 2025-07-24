import threading
from PyQt5.QtWidgets import QWidget
from .UI_window import Ui_Form
from components.citrus_api import CitrusApi


class WindowGetCardsID(QWidget):
    def __init__(self):
        super(WindowGetCardsID, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.citrus = CitrusApi()

        # привязываем события нажатия клавиши
        self.ui.btn_request.clicked.connect(self.get_api_data)

    def get_api_data(self):
        category_slug = self.ui.category_slug.text()
        page_start = self.ui.start_page_text.text()
        page_end = self.ui.end_page_text.text()
        if page_start and page_end:
            try:
                page_start = int(page_start)
                page_end = int(page_end)
            except ValueError:
                self.ui.textEdit.addItem("page_start и page_end должны быть заполнены и быть целым числом!")
        else:
            self.ui.textEdit.addItem("page_start и page_end должны быть заполнены и быть целым числом!")

        thread = threading.Thread(
            target=self.citrus.get_ids,
            args=(category_slug, page_start, page_end)
        )

        thread.start()
        thread.join()  # Дождаться завершения

        self.ui.textEdit.clear()  # очищаем список
        for idd in self.citrus.cards_id:
            self.ui.textEdit.append(str(idd))
