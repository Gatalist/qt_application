from PyQt5.QtWidgets import QTableWidget, QApplication
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from components.image import ImageManager
from .UI_window import Ui_Form


class CopyableTableWidget(QTableWidget):
    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Copy):
            self.copy_selection()
        else:
            super().keyPressEvent(event)

    def copy_selection(self):
        selection = self.selectedIndexes()

        if not selection:
            return

        selection.sort(key=lambda x: (x.row(), x.column()))
        rows = {}
        for index in selection:
            item = self.item(index.row(), index.column())
            if item:
                rows.setdefault(index.row(), {})[index.column()] = item.text()

        copied_text = ''
        for row in sorted(rows):
            line = '\t'.join(rows[row].get(col, '') for col in sorted(rows[row]))
            copied_text += line + '\n'

        QApplication.clipboard().setText(copied_text.strip())


class CopyImageWorker(QThread):
    # Сигнал, который передаст результат обратно в окно
    finished = pyqtSignal(list)

    def __init__(self, manager, path):
        super().__init__()
        self.manager = manager
        self.path = path

    def run(self):
        # Запускаем тяжелую задачу в отдельном потоке
        self.manager.move_for_one_folder(self.path)
        # Когда закончили, отправляем результат через сигнал
        self.finished.emit(self.manager.move_result)


class WindowCopyImage(QWidget):
    def __init__(self):
        super(WindowCopyImage, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.image_manager = ImageManager()
        self.worker = None  # Для хранения ссылки на поток

        # Заменяем tableWidget на кастомный, чтобы работал Ctrl+C
        self.replace_table_with_copyable()

        self.ui.btn_start.clicked.connect(self.start_copy_image_process)

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
        new_table.setHorizontalHeaderLabels(["Name","Status", "Path"])
        # Добавляем в layout
        layout.addWidget(new_table)

        self.ui.tableWidget = new_table
        old_table.deleteLater()

    def start_copy_image_process(self):
        path_folder = self.ui.str_path.text()

        # Блокируем кнопку, чтобы не запустили дважды
        self.ui.btn_start.setEnabled(False)
        self.ui.label_7.setText("Обработка... ⏳")

        self.ui.tableWidget.clearContents()

        self.worker = CopyImageWorker(self.image_manager, path_folder)
        # Подключаем функцию, которая выполнится ПОСЛЕ завершения
        self.worker.finished.connect(self.on_resize_finished)
        # Запускаем (теперь БЕЗ .join(), интерфейс будет работать!)
        self.worker.start()

    def on_resize_finished(self, result_data):
        # Эта функция сработает сама, когда поток закончит работу
        print("START ADD DATA FOR TABLE")
        self.ui.label_7.setText("Готово ✅")
        self.ui.btn_start.setEnabled(True)

        self.ui.tableWidget.clearContents()
        self.add_data_to_table(result_data)

    def add_data_to_table(self, data: list[dict]):
        self.ui.tableWidget.setRowCount(len(data))
        for row_index, card_data in enumerate(data):
            self.ui.tableWidget.setItem(row_index, 0, QTableWidgetItem(card_data['name']))
            self.ui.tableWidget.setItem(row_index, 1, QTableWidgetItem(card_data['status']))
            self.ui.tableWidget.setItem(row_index, 2, QTableWidgetItem(str(card_data['path'])))
