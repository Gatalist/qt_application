from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot

from .UI_window import Ui_Form
from components import excel_document, write_excel_document



class WindowMoveSearchCell(QWidget):
    def __init__(self):
        super(WindowMoveSearchCell, self).__init__()
        
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # привязываем события | чтение документа
        self.ui.btn_start.clicked.connect(self.btn_start_work)
        
    # обработка результата - кнопка начать
    def btn_start_work(self):
        cell_from = self.ui.lineEdit_from.text()
        cell_to = self.ui.lineEdit_to.text()
        text = self.ui.search_text.text()
        print(cell_to, text)
        read = write_excel_document.move_search_text_to_other_cell(excel_document, cell_from, cell_to, text)
        for string in read:
            self.ui.textEdit.append(string)
