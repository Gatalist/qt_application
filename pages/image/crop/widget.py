from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from components.copyable_table import CopyableTableWidget
from components.image import ImageManager
from components.universal_worker import UniversalWorker
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

        # Заменяем tableWidget на кастомный, чтобы работал Ctrl+C
        self.replace_table_with_copyable()

        self.ui.btn_start.clicked.connect(self.start_crop_process)

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

    def start_crop_process(self):
        path_folder = self.ui.str_path.text()
        padding_space = self.ui.end_page_text.text()

        try:
            padding_space = int(padding_space)

        except ValueError:
            print("page_start и page_end должны быть целыми числами")
            return

        self.ui.tableWidget.clearContents()
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
