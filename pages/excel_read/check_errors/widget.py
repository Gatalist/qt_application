from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot

from .UI_window import Ui_Form
from components import excel_document, read_excel_document


class WindowCheckErrors(QWidget):
    def __init__(self):
        super(WindowCheckErrors, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # привязываем события | чтение документа
        self.ui.btn_start.clicked.connect(self.btn_start_work)
        
    # обработка результата - кнопка начать
    def btn_start_work(self):
        self.ui.textEdit.clear()
        column_name = self.ui.comboBox.currentText()
        list_data = excel_document.get_rows_from_column(column_name)
        read = read_excel_document.check_error_in_column(list_data)
        for string in read:
            self.ui.textEdit.append(string)

    # выводим все колонки документа в осписок нашего окна
    def add_list_columns(self, data_list):
        self.ui.comboBox.clear() # очищаем список
        for column in data_list:
            self.ui.comboBox.addItem(column)

    @pyqtSlot(object)
    def receive_object_document(self, data):
        # выведем список колонок в документе в наш виджет
        self.add_list_columns(data.list_column)
