from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
import threading
from .UI_window import Ui_Form
from .speed_test_api import SpeedPageTest
from components.copyable_table import CopyableTableWidget


class WindowGetSpeedTest(QWidget):
    def __init__(self):
        super(WindowGetSpeedTest, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.citrus = SpeedPageTest()

        # Заменяем tableWidget на кастомный, чтобы работал Ctrl+C
        self.replace_table_with_copyable()

        self.ui.btn_request.clicked.connect(self.get_api_data)

    def replace_table_with_copyable(self):
        old_table = self.ui.tableWidget
        parent = old_table.parent()
        layout = parent.layout()
        font = old_table.font()

        # Создаём кастомную таблицу
        new_table = CopyableTableWidget(parent)
        new_table.horizontalHeader().setStretchLastSection(True)
        new_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        new_table.setObjectName("tableWidget")
        new_table.setFont(font)
        new_table.setColumnCount(8)
        new_table.setHorizontalHeaderLabels([
            "ID", "url", "first_contentful_paint", "largest_contentful_paint", "total_blocking_time",
            "cumulative_layout_shift", "speed_index", "performance"
        ])
        # Добавляем в layout
        layout.addWidget(new_table)

        self.ui.tableWidget = new_table
        self.setLayout(layout)
        old_table.deleteLater()

    def get_api_data(self):
        category_slug = self.ui.category_slug.text()
        page_start = self.ui.start_page_text.text()
        page_end = self.ui.end_page_text.text()
        version = self.ui.select_version.currentData()

        try:
            page_start = int(page_start)
            page_end = int(page_end)
        except ValueError:
            print("page_start и page_end должны быть целыми числами")
            return

        print("START GET CARD FOR API")

        thread_api = threading.Thread(
            target=self.citrus.get_data,
            args=(category_slug, page_start, page_end)
        )

        thread_api.start()
        thread_api.join()

        print("START GET SPEED TEST")

        thread_speed = threading.Thread(
            target=self.citrus.get_result_speed_test,
            args=(version, self.citrus.cards_data)
        )

        thread_speed.start()
        thread_speed.join()

        print("START ADD DATA FOR TABLE")

        self.ui.tableWidget.clearContents()
        self.add_data_to_table(self.citrus.cards_speed_test)

    def add_data_to_table(self, data):
        print("CARD_DATA:", data)
        self.ui.tableWidget.setRowCount(len(data))

        for row_index, card_data in enumerate(data):
            self.ui.tableWidget.setItem(row_index, 0, QTableWidgetItem(str(card_data['id'])))
            self.ui.tableWidget.setItem(row_index, 1, QTableWidgetItem(card_data['url']))
            self.ui.tableWidget.setItem(row_index, 2, QTableWidgetItem(str(card_data['first_contentful_paint'])))
            self.ui.tableWidget.setItem(row_index, 3, QTableWidgetItem(str(card_data['largest_contentful_paint'])))
            self.ui.tableWidget.setItem(row_index, 4, QTableWidgetItem(str(card_data['total_blocking_time'])))
            self.ui.tableWidget.setItem(row_index, 5, QTableWidgetItem(str(card_data['cumulative_layout_shift'])))
            self.ui.tableWidget.setItem(row_index, 6, QTableWidgetItem(str(card_data['speed_index'])))
            self.ui.tableWidget.setItem(row_index, 7, QTableWidgetItem(str(card_data['performance'])))
