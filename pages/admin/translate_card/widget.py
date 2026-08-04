from PyQt5.QtWidgets import QWidget, QHeaderView, QTableWidgetItem
from multiprocessing import Process, Queue
from PyQt5.QtCore import QTimer
from queue import Empty
from .UI_window import Ui_Form
from .models import CardAttribute
from components.copyable_table import CopyableTableWidget


class WindowTranslateCard(QWidget):
    def __init__(self):
        super(WindowTranslateCard, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # привязываем события | чтение документа
        self.ui.open_browser.clicked.connect(self.open_browser)

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
                # self.row_index += 1
                print("END ADDED to table")
            except Empty:
                break  # Как только очередь пуста — выходим из while

    @staticmethod
    def run_process_translate(queue, page_name, start_page, end_page, item_in_page, url_translate):
        browser = CardAttribute(queue=queue, visible=True)
        browser.create_page(page_name=page_name)
        browser.login(page_name=page_name)
        browser.start(
            page_name=page_name,
            start_page=start_page,
            checking_page=end_page,
            item_in_page=item_in_page,
            link_translate=url_translate,
        )
        browser.close()

    def open_browser(self):
        print("start_page", self.ui.start_page_text.text())
        print("end_page", self.ui.end_page_text.text())
        print("item_in_page", self.ui.item_page_text.text())
        self.ui.tableWidget.clear()
        process = Process(
            target=self.run_process_translate,
            kwargs={
                "queue": self.queue,
                "page_name": "citrus",
                "start_page": int(self.ui.start_page_text.text()),
                "end_page": int(self.ui.end_page_text.text()),
                "item_in_page": int(self.ui.item_page_text.text()),
                "url_translate": self.ui.translate_url_text.text()
            }
        )
        process.start()
