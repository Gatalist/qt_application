from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5 import QtWidgets
from .UI_window import Ui_Form
from components import excel_document, json_document


class ExcelLoader(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, file_path, excel_manager):
        super().__init__()
        self.file_path = file_path
        self.excel_manager = excel_manager

    def run(self):
        try:
            # Выполняем тяжелую загрузку
            self.excel_manager.load_data_from_file(self.file_path)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class WindowOpenFile(QWidget):
    ## ==========================================================
    ## Добавляем сигнал который будет отправлять данные в другие окна
    ## ==========================================================
    send_object_document = pyqtSignal(object)


    def __init__(self):
        super(WindowOpenFile, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # привязываем события | чтение документа
        self.ui.btn_open_xlsx.clicked.connect(self.open_excel_file)
        self.ui.btn_save_xlsx.clicked.connect(self.save_excel_file)
        self.ui.btn_open_json.clicked.connect(self.open_json_file)

        self.ui.comboBox.activated.connect(self.select_work_sheet)

    # окно выбора файла xlsx
    def open_excel_file(self):
        result = QtWidgets.QFileDialog.getOpenFileName(self, excel_document.WINDOW_EXPLORE_OPEN_NAME, './', excel_document.format_open)
        file_path = result[0] if result else None

        if file_path:  # Проверяем, что путь не пустой (пользователь не нажал "Отмена")
            # 1. Блокируем интерфейс
            self.ui.btn_open_xlsx.setEnabled(False)
            self.ui.label_open_file_xl.setText("Загрузка...")

            # 2. Создаем поток и воркер, передаем ПУТЬ (строку), а не кортеж
            self.thread = QThread()
            self.worker = ExcelLoader(file_path, excel_document)  # Передаем file_path
            self.worker.moveToThread(self.thread)

            # ... далее без изменений ...
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.on_load_finished)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.error.connect(self.on_load_error)  # Лучше создать метод для ошибки
            self.thread.start()

    def on_load_finished(self):
        # Этот метод выполнится, когда файл прочитан
        self.ui.btn_open_xlsx.setEnabled(True)
        self.ui.label_open_file_xl.setText(f"{excel_document.document} ✅")
        self.add_list_sheet_to_combo_box()
        self.send_object_document.emit(excel_document)

    def on_load_error(self, message):
        self.ui.btn_open_xlsx.setEnabled(True)
        self.ui.label_open_file_xl.setText("Ошибка при открытии!")
        QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {message}")

    # save new file
    def save_excel_file(self):
        name = QtWidgets.QFileDialog.getSaveFileName(self, excel_document.WINDOW_EXPLORE_SAVE_NAME, './', excel_document.format_open)
        string = ""
        try:
            excel_document.work_book.save(name[0])
            string = excel_document.MESSAGE_DOCUMENT_IS_SAVE
        except:
            string = excel_document.MESSAGE_FAILED_SAVE_DOCUMENT

        self.ui.label_save_file_xl.setText(string)

    # Добавляем все листы документа в comboBox
    def add_list_sheet_to_combo_box(self) -> None:
        self.ui.comboBox.clear()
        for sheet_name in excel_document.list_sheet:
            self.ui.comboBox.addItem(sheet_name)
    
    # выбираем рабочий лист документа
    def select_work_sheet(self) -> None:
        print('select worksheet')
        excel_document.active_list_to_write(self.ui.comboBox.currentText()) # получаем рабочий лист в документе
        # передаем сигнал с данными
        self.send_object_document.emit(excel_document)

    # окно выбора файла json
    def open_json_file(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, json_document.WINDOW_EXPLORE_OPEN_NAME, './', json_document.format_open)
        if file:
            if file[0]:
                json_document.load_data_from_file(file[0])
                # добавляем вывод у виджет с сылкой на файл
                self.ui.label_open_file_json.setText(f"{json_document.document} ✅")

            if not json_document.document:
                self.ui.label_open_file_json.setText(json_document.MESSAGE_DOCUMENT_IS_NOT_OPEN)
