from components.universal_worker import UniversalWorker
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import QTimer
from components.image import ImageManager
from components.copyable_table import CopyableTableWidget
from pathlib import Path
from queue import Queue
from .UI_window import Ui_Form


class WindowResizeImage(QWidget):
    def __init__(self):
        super(WindowResizeImage, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.end_page_text.setText("2500")
        self.image_manager = ImageManager()
        self.worker = None
        self.result_queue = Queue()  # Очередь для результатов
        self.timer = QTimer()  # Таймер для проверки очереди
        self.timer.timeout.connect(self.check_queue)

        self.ui.btn_start.clicked.connect(self.start_resize_process)

        self.ui.tableWidget = CopyableTableWidget.replace_table_with_copyable(
            self.ui.tableWidget,
            headers=["Name", "Status", "Path"],
            column_count=3,
            row_count=5,
            # auto_add_rows=True,
            # auto_add_require_all_columns=False,
        )

    def start_resize_process(self):
        path_folder = self.ui.str_path.text()
        max_width_img = self.ui.end_page_text.text()

        try:
            max_width_img = int(max_width_img)
        except ValueError:
            self.handle_api_error("max_width должен быть целым числом")
            return

        if max_width_img < 20:
            self.handle_api_error("max_width не может быть меньше 20")
            return

        if not self.is_existing_path(path_folder):
            self.handle_api_error("Пожалуйста, введите корректный путь (папка не найдена)")
            return

        # Блокируем кнопку, чтобы не запустили дважды
        self.ui.btn_start.setEnabled(False)
        self.ui.label_7.setText("Обработка... ⏳")

        self.ui.tableWidget.setRowCount(0)

        # Очищаем очередь
        while not self.result_queue.empty():
            self.result_queue.get()

        # Создаем поток с передачей очереди
        self.worker = UniversalWorker(
            fn=self.image_manager.resize_image,
            in_path=path_folder,
            max_width=max_width_img,
            result_queue=self.result_queue
        )

        # Подключаем функцию, которая выполнится ПОСЛЕ завершения
        self.worker.finished.connect(self.on_resize_finished)
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

    def on_resize_finished(self):
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