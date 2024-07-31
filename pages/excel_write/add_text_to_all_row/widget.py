from PyQt5.QtWidgets import QWidget

from .UI_window import Ui_Form
from components import excel_document, write_excel_document


class WindowAddAllRow(QWidget):
    def __init__(self):
        super(WindowAddAllRow, self).__init__()
        
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # привязываем события | чтение документа
        self.ui.btn_start.clicked.connect(self.btn_start_work)
        
    # обработка результата - кнопка начать
    def btn_start_work(self):
        cell_to = self.ui.lineEdit_to.text()
        text = self.ui.search_text.text()
        print(cell_to, text)
        read = write_excel_document.add_text_to_cell(excel_document, cell_to, text, 'all')
        for string in read:
            self.ui.textEdit.append(string)
