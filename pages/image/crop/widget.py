from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import QTimer
from components.copyable_table import CopyableTableWidget
from components.image import ImageManager
from components.universal_worker import UniversalWorker
from pathlib import Path
from queue import Queue
from .UI_window import Ui_Form


class WindowCropImage(QWidget):
    def __init__(self):
        super(WindowCropImage, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.end_page_text.setText("10")
        self.image_manager = ImageManager()
        self.worker = None
        self.result_queue = Queue()  # Очередь для результатов
        self.timer = QTimer()  # Таймер для проверки очереди
        self.timer.timeout.connect(self.check_queue)

        self.ui.btn_start.clicked.connect(self.start_crop_process)

        self.ui.tableWidget = CopyableTableWidget.replace_table_with_copyable(
            self.ui.tableWidget,
            headers=["Name", "Status", "Path"],
            column_count=3,
            row_count=5,
            # auto_add_rows=True,
            # auto_add_require_all_columns=False,
        )

    def start_crop_process(self):
        path_folder = self.ui.str_path.text()
        padding_space = self.ui.end_page_text.text()

        try:
            padding_space = int(padding_space)
        except ValueError:
            self.handle_api_error("padding_space должен быть целым числом")
            return

        if padding_space < 0:
            self.handle_api_error("Пожалуйста, введите положительные числа.")
            return

        if not self.is_existing_path(path_folder):
            self.handle_api_error("Пожалуйста, введите корректный путь (папка не найдена)")
            return

        self.ui.tableWidget.setRowCount(0)
        self.ui.label_7.setText("Обработка... ⏳")
        self.ui.btn_start.setEnabled(False)

        # Очищаем очередь
        while not self.result_queue.empty():
            self.result_queue.get()

        self.worker = UniversalWorker(
            fn=self.image_manager.crop_space,
            in_path=path_folder,
            padding_space=padding_space,
            result_queue=self.result_queue
        )

        self.worker.finished.connect(self.on_crop_finished)
        self.worker.error.connect(lambda err: print(f"Ошибка: {err}"))

        # Запускаем таймер для периодической проверки очереди (каждые 100мс)
        self.timer.start(100)

        self.worker.start()

    def check_queue(self):
        """Проверяем очередь и добавляем данные в таблицу"""
        while not self.result_queue.empty():
            try:
                card_data = self.result_queue.get_nowait()
                self.add_row_to_table(card_data)
            except:
                break

    def add_row_to_table(self, card_data: dict):
        """Добавляет одну строку в таблицу"""
        row_index = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(row_index)
        self.ui.tableWidget.setItem(row_index, 0, QTableWidgetItem(card_data['name']))
        self.ui.tableWidget.setItem(row_index, 1, QTableWidgetItem(card_data['status']))
        self.ui.tableWidget.setItem(row_index, 2, QTableWidgetItem(str(card_data['path'])))

        # Автоматически прокручиваем к последней строке
        self.ui.tableWidget.scrollToBottom()

    def on_crop_finished(self):
        """Завершение обработки"""
        print("START ADD DATA FOR TABLE")
        self.timer.stop()  # Останавливаем таймер

        # Обрабатываем оставшиеся данные в очереди
        self.check_queue()

        self.ui.label_7.setText("Готово ✅")
        self.ui.btn_start.setEnabled(True)

    def handle_api_error(self, err):
        self.ui.btn_start.setEnabled(True)
        self.timer.stop()
        QMessageBox.critical(self, "Error", f"{err}")

    @staticmethod
    def is_existing_path(text):
        if text:
            path = Path(text)
            return path.exists()
        return False