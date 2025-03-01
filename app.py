import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from UI_window import Ui_MainWindow
from settings import Settings

# Импортируем все окна
from pages.home.open_files.widget import WindowOpenFile

from pages.excel_read.read_columns.widget import WindowReadColumns
from pages.excel_read.check_errors.widget import WindowCheckErrors
from pages.excel_read.search_text.widget import WindowSearchText
from pages.excel_read.unique_values.widget import WindowUniqueValues
from pages.excel_read.unused_value.widget import WindowUnusedValues

from pages.excel_write.move_to_another_cell.widget import WindowRemoweAnother
from pages.excel_write.move_search_to_cell.widget import WindowMoveSearchCell
from pages.excel_write.add_text_to_start_row.widget import WindowAddStartRow
from pages.excel_write.add_text_to_end_row.widget import WindowAddEndRow
from pages.excel_write.add_text_to_all_row.widget import WindowAddAllRow

from pages.admin.youtube.widget import WindowYoutube
from pages.admin.greed.widget import WindowCreateGreed
from pages.admin.translate_fields.widget import WindowTranslate
from pages.admin.translate_card.widget import WindowTranslateCard
from pages.admin.structure.widget import WindowStructure


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Добавляем текущую директорию в переменные среды
        sys.path.append(Settings.ROOT_PATH)

        # Загружаем UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Словарь кнопок и соответствующих окон
        self.menu_btn_windows = {
            self.ui.btn_open_file: WindowOpenFile(),
            self.ui.btn_read_column: WindowReadColumns(),
            self.ui.btn_check_errors: WindowCheckErrors(),
            self.ui.btn_search_text: WindowSearchText(),
            self.ui.btn_unique_values: WindowUniqueValues(),
            self.ui.menu_btn_not_use_value: WindowUnusedValues(),
            self.ui.btn_move_to_another: WindowRemoweAnother(),
            self.ui.btn_move_search_to_cell: WindowMoveSearchCell(),
            self.ui.btn_add_text_to_start: WindowAddStartRow(),
            self.ui.btn_add_text_to_end: WindowAddEndRow(),
            self.ui.btn_add_text_to_all: WindowAddAllRow(),
            self.ui.menu_btn_youtube: WindowYoutube(),
            self.ui.menu_btn_create_greed: WindowCreateGreed(),
            self.ui.menu_btn_translate_attr: WindowTranslate(),
            self.ui.menu_btn_translate_card: WindowTranslateCard(),
            self.ui.menu_btn_structure: WindowStructure()
        }

        # Привязываем кнопки к функции открытия окон
        for btn in self.menu_btn_windows:
            btn.clicked.connect(self.show_selected_window)

        # Показываем стартовое окно
        self.show_home_window()

        # Подключаем сигналы
        self.ui.tabWidget.tabCloseRequested.connect(self.close_tab)
        self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)

        # Связываем передачу объекта документа со всеми окнами
        self.menu_btn_windows[self.ui.btn_open_file].send_object_document.connect(self.receive_object_document)

    def show_home_window(self):
        """Открывает главное окно при запуске."""
        self.show_window(self.ui.btn_open_file.text(), self.menu_btn_windows[self.ui.btn_open_file])

    def show_selected_window(self):
        """Открывает окно, соответствующее нажатой кнопке."""
        button = self.sender()
        self.show_window(button.text(), self.menu_btn_windows[button])

    def show_window(self, title, window):
        """Логика открытия окна с проверкой вкладок."""
        result = self.open_tab_flag(title)
        self.set_btn_checked(title)
        if result[0]:
            self.ui.tabWidget.setCurrentIndex(result[1])
        else:
            self.ui.tabWidget.addTab(window, title)
            self.ui.tabWidget.setCurrentWidget(window)
            self.ui.tabWidget.setVisible(True)

    def close_tab(self, index):
        """Закрывает вкладку и возвращает на стартовое окно, если вкладок больше нет."""
        self.ui.tabWidget.removeTab(index)
        if self.ui.tabWidget.count() == 0:
            self.show_home_window()

    def open_tab_flag(self, tab):
        """Проверяет, открыта ли уже вкладка с таким именем."""
        for i in range(self.ui.tabWidget.count()):
            if self.ui.tabWidget.tabText(i) == tab:
                return True, i
        return False,

    def set_btn_checked(self, title):
        """Устанавливает состояние нажатой кнопки."""
        for btn in self.menu_btn_windows:
            btn.setChecked(btn.text() == title)

    def on_tab_changed(self, index):
        """Выводит в консоль информацию о смене вкладки."""
        print(f"Активная вкладка: {index} - {self.ui.tabWidget.tabText(index)}")

    def receive_object_document(self, document):
        """Передает объект документа во все связанные окна."""
        for window in [
            self.menu_btn_windows[self.ui.btn_read_column],
            self.menu_btn_windows[self.ui.btn_check_errors],
            self.menu_btn_windows[self.ui.btn_search_text],
            self.menu_btn_windows[self.ui.btn_unique_values],
            self.menu_btn_windows[self.ui.menu_btn_not_use_value]
        ]:
            window.receive_object_document(document)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
