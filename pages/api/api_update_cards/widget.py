import threading
from time import sleep
from PyQt5.QtWidgets import QWidget
from .UI_window import Ui_Form

from components.browser import Browser


class WindowUpdateCards(QWidget, Browser):
    def __init__(self):
        super(WindowUpdateCards, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # привязываем события нажатия клавиши
        self.ui.btn_request.clicked.connect(self.update_cards)

        self.updated_cards = []

    def update_cards(self):
        card_ids_text = self.ui.textEdit_ids.toPlainText()
        if not card_ids_text:
            self.ui.textEdit_res.addItem("Введите ID!")
            return None

        card_ids_split = card_ids_text.split('\n')
        # for card_id in card_ids_split:
        if card_ids_split[-1] == '':
            card_ids_split.pop()

        errors = []
        card_ids = []
        for card_id in card_ids_split:
            error = f"{card_id} - не является числом!"
            if card_id in (" ", "   ", "\t"):
                self.ui.textEdit_res.addItem(error)
                errors.append(error)
                continue

            if int(card_id):
                card_ids.append(card_id)
            else:
                errors.append(error)

        if not errors:
            print(card_ids_split)

            thread = threading.Thread(
                target=self.update_index_card,
                args=(card_ids,)
            )

            thread.start()
            thread.join()  # Дождаться завершения

            self.ui.textEdit_res.clear()  # очищаем список
            for idd in self.updated_cards:
                self.ui.textEdit_res.append(str(idd))

    def update_index_card(self, card_ids: list[int]):
        page_name = "update_cards"
        self.create_page(page_name)
        self.login(page_name=page_name)

        for _id in card_ids:
            new_url = f"{self.base_url_admin}/contento/content/tovar/card/{_id}/index/update"
            result = self.open_url(page_name=page_name, link=new_url, wait_until="domcontentloaded")

            request_status = result.ok

            if request_status:
                print(f"Failed to update card with ID {id}. Status code: {request_status}")
            self.updated_cards.append(f"{_id} = status {request_status}")
            sleep(2)
