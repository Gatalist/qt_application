from PyQt5.QtWidgets import QTableWidget, QApplication
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from multiprocessing import Process, Queue
from PyQt5.QtCore import QTimer
from enum import Enum
from .UI_window import Ui_Form
from .catalog import Category


class Methods(str, Enum):
    ALL = "Название всех категорий",
    BREEDING = "Название категорий на выведение",
    STRUCTURE = "Генерация всей структуры категорий",


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


class WindowStructure(QWidget):
    def __init__(self):
        super(WindowStructure, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.save_json_folder = None
        self.queue = Queue()
        self.structure = None

        self.add_method_to_combobox()

        # привязываем события
        self.ui.btn_generate.clicked.connect(self.generate)

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
        new_table.setGeometry(geometry)
        new_table.setObjectName("tableWidget")
        new_table.setFont(font)
        new_table.setColumnCount(1)
        new_table.setHorizontalHeaderLabels([
            "Name"
        ])
        # Добавляем в layout
        layout.addWidget(new_table)

        self.ui.tableWidget = new_table
        old_table.deleteLater()

    def check_queue(self):
        while not self.queue.empty():
            msg = self.queue.get()
            print("queue:", msg)
            self.structure = msg
            self.ui.message.setText("Готово ✅")



    @staticmethod
    def run_process_get_structure(page_name, queue):
        category = Category()
        print("start ---->")
        category.create_page(page_name=page_name)
        category.login(page_name=page_name)

        datatable = category.get_structure(page_name=page_name, link=category.link_structure)
        category.add_category_to_main(page_name=page_name, datatable=datatable)
        print("structure:", category.structure)
        queue.put(category.structure)
        category.save_structure_to_json()
        print("structure: save")

    @staticmethod
    def run_process_get_all_names(lang: str, all_cat: bool):
        cats = Category()
        cats_data = cats.get_structure_from_json()
        return cats.get_categories_name(dict_data=cats_data, lang=lang, all_cat=all_cat)

    def generate(self):
        method = self.ui.comboBoxMethod.currentText()
        language = self.ui.comboBoxLang.currentText()

        print("method:", method)
        if method == Methods.STRUCTURE:
            self.ui.message.setText("")
            process = Process(target=self.run_process_get_structure, kwargs={"page_name": "citrus", "queue": self.queue})
            process.start()

        if method == Methods.BREEDING:
            self.ui.message.setText("")
            data = self.run_process_get_all_names(lang=language, all_cat=False)
            self.ui.tableWidget.clearContents()
            self.add_data_to_table(data)
            self.ui.message.setText("Готово ✅")

        if method == Methods.ALL:
            self.ui.message.setText("")
            data = self.run_process_get_all_names(lang=language, all_cat=True)
            self.ui.tableWidget.clearContents()
            self.add_data_to_table(data)
            self.ui.message.setText("Готово ✅")

    def add_method_to_combobox(self):
        list_method = [
            Methods.STRUCTURE,
            Methods.BREEDING,
            Methods.ALL,
        ]

        self.ui.comboBoxMethod.clear()
        for method in list_method:
            self.ui.comboBoxMethod.addItem(method)

    def add_data_to_table(self, data):
        print("CARD_DATA:", data)
        self.ui.tableWidget.setRowCount(len(data))

        for row_index, card_data in enumerate(data):
            self.ui.tableWidget.setItem(row_index, 0, QTableWidgetItem(card_data))