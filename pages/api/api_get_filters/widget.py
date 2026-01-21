from PyQt5.QtWidgets import QTableWidget, QApplication
from PyQt5.QtGui import QKeySequence
import threading
from components.citrus_api import CitrusApi
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from .UI_window import Ui_Form
from components.copyable_table import CopyableTableWidget


class WindowGetFilterData(QWidget):
    def __init__(self):
        super(WindowGetFilterData, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.citrus = CitrusApi()
        self.row = 1

        # Заменяем tableWidget на кастомный, чтобы работал Ctrl+C
        self.replace_table_with_copyable()

        self.ui.btn_request.clicked.connect(self.get_api_data)

    def replace_table_with_copyable(self):
        old_table = self.ui.tableWidget
        parent = old_table.parent()
        layout = parent.layout()
        geometry = old_table.geometry()
        font = old_table.font()

        # Создаём кастомную таблицу
        new_table = CopyableTableWidget(parent)
        new_table.setGeometry(geometry)
        new_table.setObjectName("tableWidget")
        new_table.setFont(font)
        new_table.setColumnCount(3)
        new_table.setHorizontalHeaderLabels([
            "FilterGroup", "FilterName", "FilterURL"
        ])
        # Добавляем в layout
        layout.addWidget(new_table)

        self.ui.tableWidget = new_table
        old_table.deleteLater()

    def get_api_data(self):
        category_slug = self.ui.category_slug.text()

        thread = threading.Thread(
            target=self.citrus.get_filters,
            args=(category_slug,)
        )

        thread.start()
        thread.join()

        print("START ADD DATA FOR TABLE")

        self.ui.tableWidget.clearContents()
        self.add_data_to_table(self.citrus.category_filters)

    def add_data_to_table(self, filters):
        table = self.ui.tableWidget

        for _filter in filters:
            print("FILTER:", _filter)
            filter_group = _filter.get('label', '')

            row = table.rowCount()  # номер новой строки
            table.insertRow(row)  # ДОБАВЛЯЕМ строку

            table.setItem(row, 0, QTableWidgetItem(filter_group))
            table.setItem(row, 1, QTableWidgetItem(''))
            table.setItem(row, 2, QTableWidgetItem(''))

            for item in _filter.get('items', []):
                filter_name = item.get('label', '')
                filter_url = item.get('url', '')

                row = table.rowCount()  # номер новой строки
                table.insertRow(row)  # ДОБАВЛЯЕМ строку

                table.setItem(row, 0, QTableWidgetItem(''))
                table.setItem(row, 1, QTableWidgetItem(filter_name))
                table.setItem(row, 2, QTableWidgetItem(filter_url))
