from components.universal_worker import UniversalWorker
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from components.image import ImageManager
from components.copyable_table import CopyableTableWidget
from .UI_window import Ui_Form


class WindowResizeImage(QWidget):
    def __init__(self):
        super(WindowResizeImage, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.end_page_text.setText("2500")
        self.image_manager = ImageManager()
        self.worker = None # Для хранения ссылки на поток

        # Заменяем tableWidget на кастомный, чтобы работал Ctrl+C
        self.replace_table_with_copyable()

        self.ui.btn_start.clicked.connect(self.start_resize_process)

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

    def start_resize_process(self):
        path_folder = self.ui.str_path.text()
        max_width_img = self.ui.end_page_text.text()

        try:
            max_width_img = int(max_width_img)
        except ValueError:
            return

        # Блокируем кнопку, чтобы не запустили дважды
        self.ui.btn_start.setEnabled(False)
        self.ui.label_7.setText("Обработка... ⏳")

        self.ui.tableWidget.clearContents()
        self.ui.tableWidget.setRowCount(0)
        
        # Создаем поток
        self.worker = UniversalWorker(
            fn=self.image_manager.resize_image,
            in_path=path_folder,
            max_width=max_width_img
        )
        # Подключаем функцию, которая выполнится ПОСЛЕ завершения
        self.worker.finished.connect(self.on_resize_finished)
        self.worker.error.connect(lambda err: print(f"Ошибка: {err}"))
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
