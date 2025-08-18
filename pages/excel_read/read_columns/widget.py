from PyQt5.QtWidgets import QWidget, QAction, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QTextCharFormat, QColor, QTextCursor

from .UI_window import Ui_Form
from components import excel_document, read_excel_document


class FindDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Найти")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()
        hLayout = QHBoxLayout()

        self.findLabel = QLabel("Найти:")
        self.findLineEdit = QLineEdit()
        self.findButton = QPushButton("Найти далее")
        self.findButton.clicked.connect(self.accept)

        hLayout.addWidget(self.findLabel)
        hLayout.addWidget(self.findLineEdit)

        mainLayout.addLayout(hLayout)
        mainLayout.addWidget(self.findButton)
        self.setLayout(mainLayout)

    def get_text(self):
        return self.findLineEdit.text()


class WindowReadColumns(QWidget):
    def __init__(self):
        super(WindowReadColumns, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # привязываем события | чтение документа
        self.ui.btn_start.clicked.connect(self.btn_start_work)
        self.ui.btn_find.clicked.connect(self.show_find_dialog)

    def show_find_dialog(self):
        print("show find_dialog")
        find_dialog = FindDialog(self)
        if find_dialog.exec_() == QDialog.Accepted:
            text_to_find = find_dialog.get_text()
            if text_to_find:
                self.find_and_highlight(text_to_find)

    def find_and_highlight(self, text):
        # Удаляем предыдущее форматирование
        self.ui.textEdit.setPlainText(self.ui.textEdit.toPlainText())

        # Создаем формат для выделения
        _format = QTextCharFormat()
        _format.setBackground(QColor("red"))

        cursor = self.ui.textEdit.document().find(text)

        while not cursor.isNull():
            cursor.mergeCharFormat(_format)
            cursor = self.ui.textEdit.document().find(text, cursor)

    # обработка результата - кнопка начать
    def btn_start_work(self):
        self.ui.textEdit.clear()
        column_name = self.ui.comboBox.currentText()
        list_data = excel_document.get_rows_from_column(column_name)
        read = read_excel_document.read_list_data_row(list_data)
        for string in read:
            self.ui.textEdit.append(string)

    # выводим все колонки документа в осписок нашего окна
    def add_list_columns(self, data_list):
        self.ui.comboBox.clear()  # очищаем список
        for column in data_list:
            self.ui.comboBox.addItem(column)

    @pyqtSlot(object)
    def receive_object_document(self, data):
        # выведем список колонок в документе в наш виджет
        self.add_list_columns(data.list_column)
