from PyQt5.QtWidgets import QWidget, QFileDialog, QHeaderView, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from .UI_window import Ui_Form
from components import excel_document, write_excel_document
from components.copyable_table import CopyableTableWidget


class WindowGetRowsById(QWidget):
    def __init__(self):
        super(WindowGetRowsById, self).__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # привязываем события | чтение документа
        self.ui.btn_start.clicked.connect(self.btn_start_work)
        self.ui.btn_save_rows_xlsx.clicked.connect(self.save_excel_file)

        self.table_row_index = 1
        self.replace_table_with_copyable()
        self.folder = ''


    def replace_table_with_copyable(self):
        old_table = self.ui.tableWidget
        parent = old_table.parent()
        layout = parent.layout()
        font = old_table.font()

        # Создаём кастомную таблицу
        new_table = CopyableTableWidget(parent)
        new_table.verticalHeader().setVisible(False)
        new_table.horizontalHeader().setStretchLastSection(True)
        new_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        new_table.setObjectName("tableWidget")
        new_table.setFont(font)
        new_table.setColumnCount(2)
        new_table.setHorizontalHeaderLabels([
            "№ строки в таблице", "IDD",
        ])
        # Добавляем в layout
        layout.addWidget(new_table)

        self.ui.tableWidget = new_table
        self.setLayout(layout)
        old_table.deleteLater()

    # обработка результата - кнопка начать
    def btn_start_work(self):
        if not self.folder:
            self.message(
                title="Выберите папку",
                text="Не выбрана папка для сохранения",
                info=""
            )
        else:
            text = self.ui.textEdit.toPlainText()
            list_id = [line.strip() for line in text.splitlines() if line.strip()]  # убираем пустые строки и пробелы
            print(list_id)
            cell_id = 'A'
            read = write_excel_document.copy_row_by_id(document=excel_document, cell_id=cell_id, list_id=list_id, path_save=self.folder)

            for string in read:
                print("return_string:", string)
                row_position = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row_position)
                self.ui.tableWidget.setItem(row_position, 0, QTableWidgetItem(string[0]))
                self.ui.tableWidget.setItem(row_position, 1, QTableWidgetItem(string[1]))

            self.ui.label_finish.setText("✅ Сохранено в файл")

    # save new file
    def save_excel_file(self):
        options = QFileDialog.Options()  # Создание объекта options
        options |= QFileDialog.ShowDirsOnly  # Добавление флага ShowDirsOnly
        folder = QFileDialog.getExistingDirectory(self, "Select Directory", "", options=options)
        if folder:
            print("[ + ] folder ->", folder)
            self.folder = folder
            self.ui.label_save_file_xl.setText(folder)

    # Окно сообщения об ошибке
    def message(self, title, text, info):
        dialog = QMessageBox()
        dialog.setWindowTitle(title)
        dialog.setText(text)
        dialog.setInformativeText(info)
        dialog.setStandardButtons(QMessageBox.Cancel)
        dialog.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        dialog.exec_()
