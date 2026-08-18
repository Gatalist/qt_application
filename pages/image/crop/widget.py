from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QMessageBox
from components.copyable_table import CopyableTableWidget
from components.image import ImageManager
from components.universal_worker import UniversalWorker
from pathlib import Path
from .UI_window import Ui_Form


class WindowCropImage(QWidget):
    def __init__(self):
        super(WindowCropImage, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.end_page_text.setText("10")
        self.image_manager = ImageManager()
        self.worker = None  # Для хранения ссылки на поток
        self.thread = None

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

        self.worker = UniversalWorker(
            fn=self.image_manager.crop_space,
            in_path=path_folder,
            padding_space=padding_space
        )
        # Подключаем функцию, которая выполнится ПОСЛЕ завершения
        self.worker.finished.connect(self.on_crop_finished)
        self.worker.error.connect(lambda err: print(f"Ошибка: {err}"))
        # Запускаем (теперь БЕЗ .join(), интерфейс будет работать!)
        self.worker.start()

    def on_crop_finished(self, result_data):
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

    def handle_api_error(self, err):
        self.ui.btn_start.setEnabled(True)
        QMessageBox.critical(self, "Error", f"{err}")

    @staticmethod
    def is_existing_path(text):
        if text:
            path = Path(text)
            return path.exists()
        return False
