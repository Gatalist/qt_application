from time import sleep
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QObject, pyqtSignal
from .UI_window import Ui_Form
# from components.browser import Browser


class UpdateCardsWorker(QObject):
    log = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, card_ids): # Только один аргумент — список ID
        super().__init__()
        self.card_ids = card_ids

    def run(self):
        # Создаем экземпляр браузера прямо ВНУТРИ потока
        # ВАЖНО: Browser должен быть доступен для импорта или инициализации здесь
        from components.browser import Browser 
        browser_instance = Browser() 

        try:
            page_name = "update_cards"
            browser_instance.create_page(page_name)
            browser_instance.login(page_name=page_name)

            for card_id in self.card_ids: # Теперь self.card_ids — это точно список
                new_url = f"{browser_instance.base_url_admin}/contento/content/tovar/card/{card_id}/index/update"
                result = browser_instance.open_url(page_name=page_name, link=new_url)
                print("result:", result)
                # print("status_code:", result.status, type(result.status))
                # if result.status == 200:
                self.log.emit(f"{card_id} = ✅ updated")
                # else:
                #     self.log.emit(f"{card_id} = ⚠️ error (status: {result.status})")
                sleep(2)

        except Exception as e:
            self.log.emit(f"Ошибка внутри потока: {e}")
        finally:
            browser_instance.close() 
            self.finished.emit()


class WindowUpdateCards(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.btn_request.clicked.connect(self.update_cards)

        self.thread = None
        self.worker = None

    def update_cards(self):

        if self.thread is not None and self.thread.isRunning():
            return
        
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
        self.ui.label_7.setText("Обработка... ⏳")

        self.thread = QThread()
        self.worker = UpdateCardsWorker(card_ids)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.log.connect(self.ui.textEdit_res.append)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        def on_finished():
            self.thread = None
            self.ui.label_7.setText("Готово ✅")
            self.ui.btn_request.setEnabled(True)
            
        self.thread.finished.connect(on_finished)

        self.thread.start()
