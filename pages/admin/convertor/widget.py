from PyQt5.QtWidgets import QWidget, QHeaderView, QTableWidgetItem
from .UI_window import Ui_Form
from components import excel_document, write_excel_document
from components.convertor import Convertor
from components.copyable_table import CopyableTableWidget
from components.convertor import Units


class WindowConvertor(QWidget):
    def __init__(self):
        super(WindowConvertor, self).__init__()

        self.convertor = Convertor()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # привязываем события | чтение документа
        self.ui.btn_start.clicked.connect(self.btn_start_work)

        self.table_row_index = 1

        self.replace_table_with_copyable()
        self.render_combo_box()

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
        new_table.setColumnCount(3)
        new_table.setHorizontalHeaderLabels([
            "№ строки в таблице", "Исходный текст", "Результат"
        ])
        # Добавляем в layout
        layout.addWidget(new_table)

        self.ui.tableWidget = new_table
        self.setLayout(layout)
        old_table.deleteLater()

    def render_combo_box(self):
        self.ui.comboBoxUnits.clear()  # очищаем список
        for unit in Units:
            _unit = str(unit.value)
            self.ui.comboBoxUnits.addItem(_unit)
            print("add unit:", _unit)

    # обработка результата - кнопка начать
    def btn_start_work(self):
        cell_from = self.ui.lineEdit_from.text()
        cell_to = self.ui.lineEdit_to.text()
        select_unit = self.ui.comboBoxUnits.currentText()
        print("select_unit:", select_unit)

        read = write_excel_document.convert_units(document=excel_document, cell_data=cell_from, cell_result=cell_to, select_unit=select_unit)

        for string in read:
            print("return_string:", string)
            row_position = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row_position)
            self.ui.tableWidget.setItem(row_position, 0, QTableWidgetItem(string[0]))
            self.ui.tableWidget.setItem(row_position, 1, QTableWidgetItem(string[1]))
            self.ui.tableWidget.setItem(row_position, 2, QTableWidgetItem(string[2]))