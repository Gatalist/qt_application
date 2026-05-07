from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from components.citrus_api import CitrusApi
from components.copyable_table import CopyableTableWidget
from .UI_window import Ui_Form


class ApiWorker(QObject):
    data_ready = pyqtSignal(list)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, citrus_api, category_slug):
        super().__init__()
        self.citrus = citrus_api
        self.category_slug = category_slug

    def run(self):
        try:
            # Выполняем тяжелый запрос к API
            self.citrus.get_filters(self.category_slug)
            # Передаем результат через сигнал
            self.data_ready.emit(self.citrus.category_filters)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()


class WindowGetFilterData(QWidget):
    def __init__(self):
        super(WindowGetFilterData, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.citrus = CitrusApi()
        self.row = 1

        # Заменяем tableWidget на кастомный, чтобы работал Ctrl+C
        self.replace_table_with_copyable()

        self.ui.btn_request.clicked.connect(self.start_api_thread)

        # Храним ссылки на поток и воркер, чтобы их не удалил сборщик мусора
        self.thread = None
        self.worker = None

    def replace_table_with_copyable(self):
        old_table = self.ui.tableWidget
        parent = old_table.parent()
        layout = parent.layout()
        geometry = old_table.geometry()
        font = old_table.font()

        # Создаём кастомную таблицу
        new_table = CopyableTableWidget(parent)
        new_table.setGeometry(geometry)
        new_table.setObjectName("tableWidget")
        new_table.setFont(font)
        new_table.setColumnCount(3)
        new_table.setHorizontalHeaderLabels([
            "FilterGroup", "FilterName", "FilterURL"
        ])
        # Добавляем в layout
        layout.addWidget(new_table)

        self.ui.tableWidget = new_table
        old_table.deleteLater()

    def start_api_thread(self):
        category_slug = self.ui.category_slug.text().strip()

        if not category_slug.startswith("/") or not category_slug.endswith("/"):
            self.handle_api_error("category_slug должен начинаться и заканчиваться на '/'")
            return

        # 1. Сначала полностью очищаем таблицу, чтобы пользователь видел, что запрос начался
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.clearContents()

        # 2. Блокируем кнопку, чтобы не наплодить потоков
        self.ui.btn_request.setEnabled(False)

        # Создаем поток и воркер
        self.thread = QThread()
        self.worker = ApiWorker(self.citrus, category_slug)
        self.worker.moveToThread(self.thread)

        # Подключаем сигналы
        self.thread.started.connect(self.worker.run)
        self.worker.data_ready.connect(self.add_data_to_table)
        self.worker.error.connect(self.handle_api_error)

        # Правильное завершение
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(lambda: self.ui.btn_request.setEnabled(True))

        self.thread.start()

    def handle_api_error(self, err):
        self.ui.btn_request.setEnabled(True)
        QMessageBox.critical(self, "Error", f"{err}")

    def add_data_to_table(self, filters):
        print("START ADD DATA FOR TABLE")
        table = self.ui.tableWidget
        table.setUpdatesEnabled(False)  # Отключаем перерисовку для скорости

        try:
            for _filter in filters:
                filter_group = _filter.get('label', '')

                # Добавляем строку группы
                row = table.rowCount()
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem(filter_group))

                for item in _filter.get('items', []):
                    filter_name = item.get('label', '')
                    filter_url = item.get('url', '')

                    # Добавляем строку фильтра
                    row = table.rowCount()
                    table.insertRow(row)
                    table.setItem(row, 0, QTableWidgetItem(''))  # Пусто в группе
                    table.setItem(row, 1, QTableWidgetItem(filter_name))
                    table.setItem(row, 2, QTableWidgetItem(filter_url))
        finally:
            table.setUpdatesEnabled(True)  # Включаем обратно
