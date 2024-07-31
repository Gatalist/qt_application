from PyQt5.QtWidgets import QWidget, QFileDialog
import threading
import os
from .UI_window import Ui_Form
from .create_table import CreateTable
from components.document import Settings


class WindowCreateSetka(QWidget):
    def __init__(self):
        super(WindowCreateSetka, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.document = None
        self.folder = None
        # Устанавливаем строку директории для чтения
        self.ui.line_save.setReadOnly(True)

        # привязываем события | чтение документа
        self.ui.btn_open_xlsx.clicked.connect(self.open_excel_file)
        self.ui.btn_select.clicked.connect(self.select_folder)
        self.ui.btn_generate_table.clicked.connect(self.save_excel_file)
    
    # окно выбира файла xlsx
    def open_excel_file(self):
        file = QFileDialog.getOpenFileName(self, Settings.WINDOW_EXPLORE_OPEN_NAME, './', Settings.EXCEL_FORMAT_OPEN)
        if file:
            if file[0]:
                self.document = CreateTable(file[0])
                # добавляем вывод у виджет с сылкой на файл
                self.ui.label_open_file_xl.setText(f"Файл открыт ✅")
            if not self.document:
                self.ui.label_open_file_xl.setText(Settings.MESSAGE_DOCUMENT_IS_NOT_OPEN)
            print(self.document.open_file)

    # # окно выбира файла xlsx
    def select_folder(self):
        options = QFileDialog.Options()  # Создание объекта options
        options |= QFileDialog.ShowDirsOnly  # Добавление флага ShowDirsOnly
        folder = QFileDialog.getExistingDirectory(self, "Select Directory", "", options=options)
        if folder:
            self.ui.line_save.setText(folder)
            self.folder = folder
            
    # save new file
    def save_excel_file(self):
        try:
            # # создаем лист на который будем записывать данные
            sheet_obj = self.document.add_new_sheet('Сетка')

            # добавляем титульную строку
            self.document.add_title_column(sheet_obj)

            # Удаляем ID, Name из списка названий колонок
            self.document.dell_id_name_from_list()

            # добавляем результаты
            self.document.for_to_colunm(sheet_obj)

            # сохраняем файл
            name = "Сгенерированая сетка.xlsx"
            # folder = os.path.join(self.folder, name)
            folder = self.folder + '/' + name
            self.document.save_xlsx(folder)
            string = Settings.MESSAGE_DOCUMENT_IS_SAVE
        except Exception as error:
            print(error)
            string = Settings.MESSAGE_FAILED_SAVE_DOCUMENT

        self.ui.label_save_file_xl.setText(string)