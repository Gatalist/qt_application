from PyQt5.QtWidgets import QWidget, QFileDialog


from .UI_window import Ui_Form
from .catalog import Category


class WindowStructure(QWidget):
    def __init__(self):
        super(WindowStructure, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.open_json_folder = None
        self.save_json_folder = None

        self.add_method_to_comboBox()

        # привязываем события | чтение документа
        self.ui.btn_open_folder.clicked.connect(self.open_folder)
        self.ui.btn_save_folder.clicked.connect(self.save_folder)
        self.ui.btn_generate.clicked.connect(self.generate)

    def generate(self):
        if self.open_json_folder and self.save_json_folder:
            method = self.ui.comboBox.currentText()
            print(method)
            category = Category(read_folder=self.open_json_folder, result_folder=self.save_json_folder)
            print(category.read_folder)
            print(category.files)

            category.run_create_category()

            self.ui.label_result.setText("Готово ✅")
        else:
            self.ui.label_result.setText("Не выбраны папки")

    # Добавляем все листы документа в comboBox
    def add_method_to_comboBox(self):
        list_method = [
            "Название категорий",
            "Категории на выведение",
            "Вся структура",
        ]

        self.ui.comboBox.clear()
        for method in list_method:
            self.ui.comboBox.addItem(method)


    # окно выбира folder
    def open_folder(self):
        options = QFileDialog.Options()  # Создание объекта options
        options |= QFileDialog.ShowDirsOnly  # Добавление флага ShowDirsOnly
        folder = QFileDialog.getExistingDirectory(self, "Select Directory", "", options=options)
        if folder:
            self.ui.line_open.setText(folder)
            self.open_json_folder = folder

    # окно выбира folder
    def save_folder(self):
        options = QFileDialog.Options()  # Создание объекта options
        options |= QFileDialog.ShowDirsOnly  # Добавление флага ShowDirsOnly
        folder = QFileDialog.getExistingDirectory(self, "Select Directory", "", options=options)
        if folder:
            self.ui.line_save.setText(folder)
            self.save_json_folder = folder
            