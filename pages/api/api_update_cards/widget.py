from time import sleep
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QObject, pyqtSignal
from .UI_window import Ui_Form
from components.browser import Browser


class UpdateCardsWorker(QObject):
    log = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, browser, card_ids):
        super().__init__()
        self.browser = browser
        self.card_ids = card_ids

    def run(self):
        try:
            page_name = "update_cards"
            self.browser.create_page(page_name)
            self.browser.login(page_name=page_name)

            for card_id in self.card_ids:
                url = f"{self.browser.base_url_admin}/contento/content/tovar/card/{card_id}/index/update"

                result = self.browser.open_url(page_name=page_name, link=url, wait_until="domcontentloaded")

                status = result.ok if result else False
                self.log.emit(f"{card_id} = status {status}")

                sleep(2)

        except Exception as e:
            self.log.emit(f"Ошибка: {e}")

        self.finished.emit()


class WindowUpdateCards(QWidget, Browser):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.btn_request.clicked.connect(self.update_cards)

        self.thread = None
        self.worker = None


    def update_cards(self):
        card_ids_text = self.ui.textEdit_ids.toPlainText().strip()

        if not card_ids_text:
            self.ui.textEdit_res.append("Введите ID!")
            return

        card_ids = []
        for line in card_ids_text.splitlines():
            if not line.isdigit():
                self.ui.textEdit_res.append(f"{line} — не число")
                return
            card_ids.append(line)

        self.ui.textEdit_res.clear()

        self.thread = QThread()
        self.worker = UpdateCardsWorker(self, card_ids)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.log.connect(self.ui.textEdit_res.append)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()
