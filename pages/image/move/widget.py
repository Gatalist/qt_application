from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QMessageBox
from components.image import ImageManager
from components.copyable_table import CopyableTableWidget
from components.universal_worker import UniversalWorker
from pathlib import Path
from .UI_window import Ui_Form


class WindowCopyImage(QWidget):
    def __init__(self):
        super(WindowCopyImage, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.image_manager = ImageManager()
        self.worker = None  # Для хранения ссылки на поток

        self.ui.btn_start.clicked.connect(self.start_copy_image_process)

        self.ui.tableWidget = CopyableTableWidget.replace_table_with_copyable(
            self.ui.tableWidget,
            headers=["Name","Status", "Path"],
            column_count=3,
            row_count=5,
            # auto_add_rows=True,
            # auto_add_require_all_columns=False,
        )

    def start_copy_image_process(self):
        path_folder = self.ui.str_path.text()

        if not self.is_existing_path(path_folder):
            self.handle_api_error("Пожалуйста, введите корректный путь (папка не найдена)")
            return

        # Блокируем кнопку, чтобы не запустили дважды
        self.ui.btn_start.setEnabled(False)
        self.ui.label_7.setText("Обработка... ⏳")

        self.ui.tableWidget.clearContents()
        self.ui.tableWidget.setRowCount(0)

        # Создаем поток
        self.worker = UniversalWorker(
            fn=self.image_manager.move_for_one_folder,
            in_path=path_folder
        )

        # Подключаем функцию, которая выполнится ПОСЛЕ завершения
        self.worker.finished.connect(self.on_resize_finished)
        self.worker.error.connect(lambda err: print(f"Ошибка: {err}"))
        # Запускаем (теперь БЕЗ .join(), интерфейс будет работать!)
        self.worker.start()

    def on_resize_finished(self, result_data):
        # Эта функция сработает сама, когда поток закончит работу
        print("START ADD DATA FOR TABLE")
        self.ui.label_7.setText("Готово ✅")
        self.ui.btn_start.setEnabled(True)

        self.ui.tableWidget.setRowCount(0)
        self.add_data_to_table(result_data)

    def add_data_to_table(self, data: list[dict]):
        self.ui.tableWidget.setRowCount(len(data))
        for row_index, card_data in enumerate(data):
            self.ui.tableWidget.setItem(row_index, 0, QTableWidgetItem(card_data['name']))
            self.ui.tableWidget.setItem(row_index, 1, QTableWidgetItem(card_data['status']))
            self.ui.tableWidget.setItem(row_index, 2, QTableWidgetItem(str(card_data['path'])))

    def handle_api_error(self, err):
        self.ui.btn_start.setEnabled(True)
        QMessageBox.critical(self, "Error", f"{err}")

    @staticmethod
    def is_existing_path(text):
        if text:
            path = Path(text)
            return path.exists()
        return False
