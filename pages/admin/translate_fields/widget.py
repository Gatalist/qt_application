from PyQt5.QtWidgets import QWidget, QApplication, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QKeySequence
from multiprocessing import Process, Queue
from PyQt5.QtCore import QTimer
from .UI_window import Ui_Form
from .models import ProductGroupValue
from queue import Empty


class CopyableTableWidget(QTableWidget):
    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Copy):
            self.copy_selection()
        else:
            super().keyPressEvent(event)

    def copy_selection(self):
        selection = self.selectedIndexes()

        if not selection:
            return

        selection.sort(key=lambda x: (x.row(), x.column()))
        rows = {}
        for index in selection:
            item = self.item(index.row(), index.column())
            if item:
                rows.setdefault(index.row(), {})[index.column()] = item.text()

        copied_text = ''
        for row in sorted(rows):
            line = '\t'.join(rows[row].get(col, '') for col in sorted(rows[row]))
            copied_text += line + '\n'

        QApplication.clipboard().setText(copied_text.strip())


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
        geometry = old_table.geometry()
        font = old_table.font()

        new_table = CopyableTableWidget(parent)
        # new_table.setGeometry(geometry)
        new_table.horizontalHeader().setStretchLastSection(True)
        new_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        new_table.setObjectName("tableWidget")
        new_table.setFont(font)
        new_table.setColumnCount(3)
        # new_table.rowCount()
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
                # self.row_index += 1
                print("END ADDED to table")
            except Empty:
                break  # Как только очередь пуста — выходим из while

    @staticmethod
    def run_process_translate(queue, page_name, start_page, end_page, item_in_page, name_option, url_translate):
        browser = ProductGroupValue(queue=queue, visible=True)
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
        process = Process(
            target=self.run_process_translate,
            kwargs={
                "queue": self.queue,
                "page_name": "citrus",
                "start_page": self.ui.start_page_text.text(),
                "end_page": self.ui.end_page_text.text(),
                "item_in_page": self.ui.item_page_text.text(),
                "name_option": self.ui.comboBox_option.currentText(),
                "url_translate": 'https://my.ctrs.com.ua/contento/translations/fields?search=&start=0&length=5&order=0&sort=asc'
            }
        )
        process.start()
        # process.join() # blocked interface

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

    # def view_result(self, result):
    #     self.ui.textEdit.append(result)