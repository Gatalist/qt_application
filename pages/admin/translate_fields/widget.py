from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, QMessageBox
from multiprocessing import Process, Queue
from PyQt5.QtCore import QTimer
from queue import Empty
from .UI_window import Ui_Form
from .models import ProductGroupValue
from components.copyable_table import CopyableTableWidget


class WindowTranslate(QWidget):
    def __init__(self):
        super(WindowTranslate, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # привязываем события | чтение документа
        self.ui.open_browser.clicked.connect(self.start_browser)
        self.add_option_name()

        self.queue = Queue()
        self.row_index = 1

        # Таймер для чтения из очереди
        self.timer = QTimer()
        self.timer.setInterval(500)  # каждые 0.5 секунды
        self.timer.timeout.connect(self.check_queue)
        self.timer.start()

        # Создаём кастомную таблицу
        self.ui.tableWidget = CopyableTableWidget.replace_table_with_copyable(
            self.ui.tableWidget,
            headers=["ID", "RU", "UK"],
            column_count=3,
            row_count=5,
            # auto_add_rows=True,
            # auto_add_require_all_columns=False,
        )

    def check_queue(self):
        while True:
            try:
                item = self.queue.get_nowait()
                print("Получено:", item)
                row_position = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row_position)
                self.ui.tableWidget.setItem(row_position, 0, QTableWidgetItem(str(item['id'])))
                self.ui.tableWidget.setItem(row_position, 1, QTableWidgetItem(str(item['ru'])))
                self.ui.tableWidget.setItem(row_position, 2, QTableWidgetItem(str(item['uk'])))
                print("END ADDED to table")
            except Empty:
                break  # Как только очередь пуста — выходим из while

    @staticmethod
    def run_process_translate(queue, page_name, start_page, end_page, item_in_page, name_option, method_translate, not_uk):
        browser = ProductGroupValue(queue=queue, visible=True, translate=method_translate, not_uk=not_uk)
        if method_translate == "Google page":
            browser.create_page(page_name=method_translate)
        browser.create_page(page_name=page_name)
        browser.login(page_name=page_name)
        browser.start(
            page_name=page_name,
            start_page=start_page,
            checking_page=end_page,
            item_in_page=item_in_page,
            name_option=name_option
        )
        browser.close()

    def start_browser(self):
        try:
            start_page = int(self.ui.start_page_text.text())
            end_page = int(self.ui.end_page_text.text())
            item_in_page = int(self.ui.item_page_text.text())
        except ValueError:
            self.handle_api_error("Пожалуйста, введите корректные числовые значения для всех полей.")
            return

        if start_page < 0 or end_page < 0 or item_in_page < 0:
            self.handle_api_error("Пожалуйста, введите положительные числа.")
            return

        self.ui.tableWidget.setRowCount(0)
        
        process = Process(
            target=self.run_process_translate,
            kwargs={
                "queue": self.queue,
                "page_name": "citrus",
                "start_page": start_page,
                "end_page": end_page,
                "item_in_page": item_in_page,
                "name_option": self.ui.comboBox_option.currentText(),
                "method_translate": self.ui.comboBox_translate.currentText(),
                "not_uk": self.ui.not_uk.isChecked()
            }
        )
        process.start()

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

    def handle_api_error(self, err):
        self.ui.open_browser.setEnabled(True)
        QMessageBox.critical(self, "Error", f"{err}")
