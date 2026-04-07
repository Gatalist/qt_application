from PyQt5.QtWidgets import QWidget, QFileDialog, QHeaderView, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from .UI_window import Ui_Form
from components import excel_document, write_excel_document
from components.copyable_table import CopyableTableWidget


class WindowSetDataById(QWidget):
    def __init__(self):
        super(WindowSetDataById, self).__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # привязываем события | чтение документа
        self.ui.btn_start.clicked.connect(self.btn_start_work)

    # обработка результата - кнопка начать
    def btn_start_work(self):
        cell_id_for_add = self.ui.lineEdit_to.text()
        add_text = self.ui.search_text.text()
        text_card_id = self.ui.textEdit_2.toPlainText()
        list_card_id = [line.strip() for line in text_card_id.splitlines() if line.strip()]
        cell_id_card = "A"
        write_data = write_excel_document.add_data_by_id(document=excel_document, cell_id_card=cell_id_card, cell_idd_add_text=cell_id_for_add, text=add_text, list_id=list_card_id)
        for string in write_data:
            self.ui.textEdit.append(string)
