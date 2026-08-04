from PyQt5.QtWidgets import QWidget, QFileDialog, QHeaderView, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from .UI_window import Ui_Form
from components import excel_document, write_excel_document


class WindowGetRowsIsColumnData(QWidget):
    def __init__(self):
        super(WindowGetRowsIsColumnData, self).__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # привязываем события | чтение документа
        self.ui.btn_start.clicked.connect(self.btn_start_work)
        self.ui.btn_save_rows_xlsx.clicked.connect(self.save_excel_file)

        self.folder = ''


    # обработка результата - кнопка начать
    def btn_start_work(self):
        if not self.folder:
            self.message(
                title="Выберите папку",
                text="Не выбрана папка для сохранения",
                info=""
            )
            return

        cell_id = self.ui.column.text()
        call_text = self.ui.name.text()
        print(f"{cell_id=}, {call_text=}")
        read = write_excel_document.copy_row_is_column_data(document=excel_document, cell_id=cell_id, call_text=call_text, path_save=self.folder)
        for string in read:
            print("return_string:", string)
            self.ui.textEdit.append(string)

        self.ui.label_4.setText("✅ Сохранено в файл")

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
