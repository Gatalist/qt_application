from PyQt5.QtWidgets import QWidget

from .UI_window import Ui_Form
from components import excel_document, write_excel_document



class WindowRemoweAnother(QWidget):
    def __init__(self):
        super(WindowRemoweAnother, self).__init__()
        
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # привязываем события | чтение документа
        self.ui.btn_start.clicked.connect(self.btn_start_work)
        
    # обработка результата - кнопка начать
    def btn_start_work(self):
        cell_from = self.ui.lineEdit_from.text()
        cell_to = self.ui.lineEdit_to.text()
        print(cell_from, cell_to)
        read = write_excel_document.move_text_to_another_cell(excel_document, cell_from, cell_to)
        for string in read:
            self.ui.textEdit.append(string)
