from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from .UI_window import Ui_Form
from components.citrus_api import CitrusApi


class ApiWorker(QObject):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, citrus_api, category_slug, page_start, page_end):
        super().__init__()
        self.citrus_api = citrus_api
        self.category_slug = category_slug
        self.page_start = page_start
        self.page_end = page_end

    def run(self):
        try:
            self.citrus_api.get_ids(self.category_slug, self.page_start, self.page_end)
            self.finished.emit(self.citrus_api.cards_id)
        except Exception as e:
            self.error.emit(str(e))


class WindowGetCardsID(QWidget):
    def __init__(self):
        super(WindowGetCardsID, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.citrus = CitrusApi()
        self.thread: QThread | None = None
        self.worker = None

        # привязываем события нажатия клавиши
        self.ui.btn_request.clicked.connect(self.get_api_data)

    def get_api_data(self):
        category_slug = self.ui.category_slug.text()
        page_start_text = self.ui.start_page_text.text()
        page_end_text = self.ui.end_page_text.text()

        if not category_slug.startswith("/") or not category_slug.endswith("/"):
            self.ui.textEdit.append("category_slug должен начинаться и заканчиваться на '/'")
            return

        if not page_start_text or not page_end_text:
            self.ui.textEdit.append("page_start и page_end должны быть заполнены!")
            return

        self.ui.label_7.setText("Обработка... ⏳")
        try:
            page_start = int(page_start_text)
            page_end = int(page_end_text)
        except ValueError:
            self.ui.textEdit.append("page_start и page_end должны быть целыми числами!")
            self.ui.label_7.setText("Ошибка... ⚠️")
            return

        self.ui.btn_request.setEnabled(False)
        self.ui.textEdit.clear()

        # Создаем поток и воркера
        self.thread = QThread()
        self.worker = ApiWorker(self.citrus, category_slug, page_start, page_end)
        self.worker.moveToThread(self.thread)

        # Соединяем сигналы
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_api_finished)
        self.worker.error.connect(self.on_api_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_api_finished(self, cards_id):
        self.ui.btn_request.setEnabled(True)
        self.ui.label_7.setText("Готово ✅")
        if not cards_id:
            self.ui.textEdit.append("Данные не найдены.")
            return
        for idd in cards_id:
            self.ui.textEdit.append(str(idd))

    def on_api_error(self, error_msg):
        self.ui.btn_request.setEnabled(True)
        self.ui.label_7.setText("Ошибка... ⚠️")
        self.ui.textEdit.append(f"Ошибка: {error_msg}")
