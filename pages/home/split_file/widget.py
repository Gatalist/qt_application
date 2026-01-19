from PyQt5.QtWidgets import QWidget
from PyQt5 import QtWidgets

from .UI_window import Ui_Form
from components.split_excel import split_excel
from settings import Settings


class WindowSplitFile(QWidget):
    def __init__(self):
        super(WindowSplitFile, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # привязываем события | чтение документа
        self.ui.btn_open_xlsx.clicked.connect(self.open_excel_file)
        self.ui.btn_save_xlsx.clicked.connect(self.select_folder)
        self.ui.btn_start.clicked.connect(self.save_excel_files)

        self.in_path = None
        self.out_path = None
        self.count_string_in_file = None

    # окно выбора файла xlsx
    def open_excel_file(self):
        if file:= QtWidgets.QFileDialog.getOpenFileName(self, Settings.WINDOW_EXPLORE_OPEN_NAME, './', Settings.EXCEL_FORMAT_OPEN):
            if file[0]:
                self.in_path = file[0]
                # добавляем вывод у виджет с сcылкой на файл
                self.ui.label_save_file_xl.setText(f"{self.in_path} ✅")

    # окно выбора folder
    def select_folder(self):
        options = QtWidgets.QFileDialog.Options()  # Создание объекта options
        options |= QtWidgets.QFileDialog.ShowDirsOnly  # Добавление флага ShowDirsOnly
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, Settings.WINDOW_EXPLORE_SAVE_NAME, "", options=options)
        if folder:
            print("[ + ] folder ->", folder)
            self.out_path = folder

    # save new file
    def save_excel_files(self):
        if not self.in_path:
            self.ui.label_save_file_xl.setText(Settings.MESSAGE_DOCUMENT_IS_NOT_OPEN)

        if not self.out_path:
            self.ui.label_save_file_xl.setText(Settings.MESSAGE_DOCUMENT_IS_NOT_SAVE_PATH)
            return

        self.count_string_in_file = self.ui.lineEdit_2.text()

        if not self.count_string_in_file:
            self.ui.label_save_file_xl.setText("Введите количество строк для документа")
            return
        else:
            self.count_string_in_file = int(self.count_string_in_file)

        try:
            split_excel(input_file=self.in_path, output_dir=self.out_path, rows_per_file=self.count_string_in_file)
            self.ui.label_save_file_xl.setText(Settings.MESSAGE_DOCUMENT_IS_SAVE)
        except Exception as e:
            self.ui.label_save_file_xl.setText(Settings.MESSAGE_FAILED_SAVE_DOCUMENT)
            print(e)
