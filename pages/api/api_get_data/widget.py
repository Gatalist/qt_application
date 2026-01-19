from PyQt5.QtWidgets import QTableWidget, QApplication
from PyQt5.QtGui import QKeySequence
import threading
from components.citrus_api import CitrusApi
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from .UI_window import Ui_Form
from components.copy_table_widget import CopyableTableWidget


class WindowGetCardsData(QWidget):
    def __init__(self):
        super(WindowGetCardsData, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.citrus = CitrusApi()

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
        new_table.setColumnCount(10)
        new_table.setHorizontalHeaderLabels([
            "ID", "Name", "Brand", "Status", "Price", "Ordering",
            "Ordering_action", "Ordering_catalog", "URL", "Image"
        ])
        # Добавляем в layout
        layout.addWidget(new_table)

        self.ui.tableWidget = new_table
        old_table.deleteLater()

    def get_api_data(self):
        category_slug = self.ui.category_slug.text()
        page_start = self.ui.start_page_text.text()
        page_end = self.ui.end_page_text.text()

        try:
            page_start = int(page_start)
            page_end = int(page_end)
        except ValueError:
            print("page_start и page_end должны быть целыми числами")
            return

        thread = threading.Thread(
            target=self.citrus.get_data,
            args=(category_slug, page_start, page_end)
        )

        thread.start()
        thread.join()

        print("START ADD DATA FOR TABLE")

        self.ui.tableWidget.clearContents()
        self.add_data_to_table(self.citrus.cards_data)

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
