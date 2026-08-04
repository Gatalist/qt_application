from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from multiprocessing import Process, Queue
from PyQt5.QtCore import QTimer
from enum import Enum
from .UI_window import Ui_Form
from .catalog import Category
from components.copyable_table import CopyableTableWidget


class Methods(str, Enum):
    ALL = "Название всех категорий"
    BREEDING = "Название категорий на выведение"
    BREEDING_NAME_URL = "Название и URL категорий на выведение"
    STRUCTURE = "Генерация всей структуры категорий"

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
        self.ui.tableWidget = CopyableTableWidget.replace_table_with_copyable(
            self.ui.tableWidget,
            headers=["Name"],
            column_count=1,
            row_count=5,
            # auto_add_rows=True,
            # auto_add_require_all_columns=False,
        )

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

    @staticmethod
    def run_process_get_all_names_and_urls(lang: str, all_cat: bool):
        cats = Category()
        cats_data = cats.get_structure_from_json()
        return cats.get_categories_name_url(dict_data=cats_data, lang=lang, all_cat=all_cat)
    
    

    def generate(self):
        method = self.ui.comboBoxMethod.currentText()
        language = self.ui.comboBoxLang.currentText()

        print("method:", method)
        if method == Methods.STRUCTURE:
            self.ui.message.setText("")
            process = Process(target=self.run_process_get_structure, kwargs={"page_name": "citrus", "queue": self.queue})
            process.start()
            # process.join() # blocked interface

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
        
        if method == Methods.BREEDING_NAME_URL:
            self.ui.message.setText("")
            data = self.run_process_get_all_names_and_urls(lang=language, all_cat=False)
            self.ui.tableWidget.clearContents()
            self.add_data_to_table_name_url(data)
            self.ui.message.setText("Готово ✅")

    def add_method_to_combobox(self):
        list_method = [
            Methods.STRUCTURE,
            Methods.BREEDING,
            Methods.BREEDING_NAME_URL,
            Methods.ALL,
        ]

        self.ui.comboBoxMethod.clear()
        for method in list_method:
            self.ui.comboBoxMethod.addItem(method)

    def add_data_to_table(self, data):
        print("CARD_DATA:", data)
        self.ui.tableWidget.clear()
        self.ui.tableWidget.setColumnCount(1)
        self.ui.tableWidget.setHorizontalHeaderLabels([
            "Name",
        ])
        self.ui.tableWidget.setRowCount(len(data))

        for row_index, card_data in enumerate(data):
            self.ui.tableWidget.setItem(row_index, 0, QTableWidgetItem(card_data))
    
    def add_data_to_table_name_url(self, data):
        print("CARD_DATA:", data)
        self.ui.tableWidget.clear()
        self.ui.tableWidget.setColumnCount(2)
        self.ui.tableWidget.setHorizontalHeaderLabels([
            "Name",
            "URL"
        ])
        self.ui.tableWidget.setRowCount(len(data))

        for row_index, card_data in enumerate(data):
            print("card_data:", card_data)
            self.ui.tableWidget.setItem(row_index, 0, QTableWidgetItem(card_data[0]))
            self.ui.tableWidget.setItem(row_index, 1, QTableWidgetItem(f'/{card_data[1]}/'))
    