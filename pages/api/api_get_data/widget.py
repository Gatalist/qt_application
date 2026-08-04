import threading
from components.citrus_api import CitrusApi
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from .UI_window import Ui_Form
from components.copyable_table import CopyableTableWidget


class ApiWorker(QObject):
    data_ready = pyqtSignal(list)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, citrus_api, category_slug, page_start, page_end, all_cards=False):
        super().__init__()
        self.citrus = citrus_api
        self.category_slug = category_slug
        self.page_start = page_start
        self.page_end = page_end
        self.all_cards = all_cards

    def run(self):
        try:
            if self.all_cards:
                self.citrus.get_data_all(self.category_slug)
            else:
                self.citrus.get_data(self.category_slug, self.page_start, self.page_end)
            self.data_ready.emit(self.citrus.cards_data)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()


class WindowGetCardsData(QWidget):
    def __init__(self):
        super(WindowGetCardsData, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.citrus = CitrusApi()

        # Заменяем tableWidget на кастомный, чтобы работал Ctrl+C
        self.ui.tableWidget = CopyableTableWidget.replace_table_with_copyable(
            self.ui.tableWidget,
            headers=[
                "ID", "Name", "Brand", "Status",
                "Price", "Ordering", "Ordering_action",
                "Ordering_catalog", "URL", "Image"
            ],
            row_count=5,
            column_count=10,
            # auto_add_rows=True,
            # auto_add_require_all_columns=False,
        )

        self.ui.btn_request.clicked.connect(self.get_api_data)

    def get_api_data(self):
        category_slug = self.ui.category_slug.text().strip()
        page_start = self.ui.start_page_text.text().strip()
        page_end = self.ui.end_page_text.text().strip()

        all_cards = self.ui.checkBox.isChecked()
        print("ALL_CARDS checkBox:", all_cards)
        # 1. Проверка на заполнение всех полей
        if not category_slug:
            QMessageBox.warning(self, "Warning", "Пожалуйста, заполните category_slug")
            return
        if not category_slug.startswith("/") or not category_slug.endswith("/"):
            QMessageBox.warning(self, "Warning", "category_slug должен начинаться и заканчиваться на '/'")
            return
        
        if all_cards == False:
            if not page_start:
                QMessageBox.warning(self, "Warning", "Пожалуйста, заполните page_start")
                return
            if not page_end:
                QMessageBox.warning(self, "Warning", "Пожалуйста, заполните page_end")
                return

            # 2. Проверка на корректность чисел
            try:
                page_start = int(page_start)
                page_end = int(page_end)
            except ValueError:
                QMessageBox.warning(self, "Warning", "page_start и page_end должны быть целыми числами")
                return
            

        # 3. Очистка таблицы и блокировка кнопки
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.clearContents()
        self.ui.btn_request.setEnabled(False)

        # Создаем поток и воркер
        self.thread = QThread()
        self.worker = ApiWorker(self.citrus, category_slug, page_start, page_end, all_cards=all_cards)
        self.worker.moveToThread(self.thread)

        # Подключаем сигналы
        self.thread.started.connect(self.worker.run)
        self.worker.data_ready.connect(self.add_data_to_table)
        self.worker.error.connect(self.handle_api_error)

        # Правильное завершение
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(lambda: self.ui.btn_request.setEnabled(True))

        self.thread.start()

    def handle_api_error(self, err):
        self.ui.btn_request.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Произошла ошибка: {err}")

    def add_data_to_table(self, data):
        print("CARD_DATA:", data)
        self.ui.tableWidget.setRowCount(len(data))

        for row_index, card_data in enumerate(data):
            self.ui.tableWidget.setItem(row_index, 0, QTableWidgetItem(str(card_data['id'])))
            self.ui.tableWidget.setItem(row_index, 1, QTableWidgetItem(card_data['name']))
            self.ui.tableWidget.setItem(row_index, 2, QTableWidgetItem(card_data['brand']))
            self.ui.tableWidget.setItem(row_index, 3, QTableWidgetItem(card_data['status']))
            self.ui.tableWidget.setItem(row_index, 4, QTableWidgetItem(str(card_data['price'])))
            self.ui.tableWidget.setItem(row_index, 5, QTableWidgetItem(str(card_data['ordering'])))
            self.ui.tableWidget.setItem(row_index, 6, QTableWidgetItem(str(card_data['ordering_action'])))
            self.ui.tableWidget.setItem(row_index, 7, QTableWidgetItem(str(card_data['ordering_catalog'])))
            self.ui.tableWidget.setItem(row_index, 8, QTableWidgetItem(card_data['url']))
            self.ui.tableWidget.setItem(row_index, 9, QTableWidgetItem(card_data['image']))
