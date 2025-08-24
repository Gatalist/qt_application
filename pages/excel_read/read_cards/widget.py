from PyQt5.QtWidgets import QWidget
from .UI_window import Ui_Form
from components import excel_document, read_excel_document


class WindowReadCards(QWidget):
    def __init__(self):
        super(WindowReadCards, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # привязываем события | чтение документа
        self.ui.btn_start_read.clicked.connect(self._start_read)

    def _start_read(self):
        self.ui.textEdit.clear()

        card_data = read_excel_document.read_card_all_attr(document=excel_document)
        for attr_data in card_data:
            for data in attr_data:
                col = data[0]
                value = data[1]

                col_name = col.split('-')[0]

                if col == 'number':
                    self.ui.textEdit.append(f'----- Строка: {value} -----\n')
                    continue

                if col == 'Юридическая информация':
                    continue

                split_text = value.split(';')
                if value and len(split_text) > 1:
                    self.ui.textEdit.append(f'{col_name}:')
                    for value in split_text:
                        self.ui.textEdit.append(f'{value}')
                    self.ui.textEdit.append('\n')
                else:
                    self.ui.textEdit.append(f'{col_name}: {value}\n')

            self.ui.textEdit.append(f'\n\n\n')

        self.ui.textEdit.append("✅ Выполнено!")
