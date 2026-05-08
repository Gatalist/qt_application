from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView
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
        self.ui.open_browser.clicked.connect(self.open_browser)
        self.add_option_name()

        self.queue = Queue()
        self.row_index = 1

        # Таймер для чтения из очереди
        self.timer = QTimer()
        self.timer.setInterval(500)  # каждые 0.5 секунды
        self.timer.timeout.connect(self.check_queue)
        self.timer.start()

        # Создаём кастомную таблицу
        old_table = self.ui.tableWidget
        parent = old_table.parent()
        layout = parent.layout()
        font = old_table.font()

        new_table = CopyableTableWidget(parent)
        new_table.horizontalHeader().setStretchLastSection(True)
        new_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        new_table.setObjectName("tableWidget")
        new_table.setFont(font)
        new_table.setColumnCount(3)
        new_table.setHorizontalHeaderLabels([
            "ID", "RU", "UK"
        ])
        # Добавляем в layout
        layout.addWidget(new_table)
        self.ui.tableWidget = new_table
        self.setLayout(layout)
        old_table.deleteLater()

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
    def run_process_translate(queue, page_name, start_page, end_page, item_in_page, name_option, url_translate):
        browser = ProductGroupValue(queue=queue, visible=True, translate="deepl")
        browser.create_page(page_name=page_name)
        browser.login(page_name=page_name)
        browser.start(
            page_name=page_name,
            start_page=start_page,
            checking_page=end_page,
            item_in_page=item_in_page,
            link_translate=url_translate,
            name_option=name_option
        )
        browser.close()

    def open_browser(self):
        self.ui.tableWidget.setRowCount(0)
        process = Process(
            target=self.run_process_translate,
            kwargs={
                "queue": self.queue,
                "page_name": "citrus",
                "start_page": int(self.ui.start_page_text.text()),
                "end_page": int(self.ui.end_page_text.text()),
                "item_in_page": int(self.ui.item_page_text.text()),
                "name_option": self.ui.comboBox_option.currentText(),
                "url_translate": 'https://my.ctrs.com.ua/contento/translations/fields?search=&start=0&length=5&order=0&sort=asc'
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
