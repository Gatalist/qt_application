import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from UI_window import Ui_MainWindow
from settings import Settings

# Импортируем все окна
from pages.home.open_files.widget import WindowOpenFile
from pages.home.split_file.widget import WindowSplitFile

from pages.excel_read.read_columns.widget import WindowReadColumns
from pages.excel_read.check_errors.widget import WindowCheckErrors
from pages.excel_read.search_text.widget import WindowSearchText
from pages.excel_read.unique_values.widget import WindowUniqueValues
from pages.excel_read.unused_value.widget import WindowUnusedValues
from pages.excel_read.read_cards.widget import WindowReadCards

from pages.excel_write.move_to_another_cell.widget import WindowMoveAnotherCell
from pages.excel_write.move_search_to_cell.widget import WindowMoveSearchCell
from pages.excel_write.copy_search_to_cell.widget import WindowCopySearchCell
from pages.excel_write.add_text_to_start_row.widget import WindowAddStartRow
from pages.excel_write.add_text_to_end_row.widget import WindowAddEndRow
from pages.excel_write.add_text_to_all_row.widget import WindowAddAllRow
from pages.excel_write.get_row_by_id.widget import WindowGetRowsById
from pages.excel_write.set_data_by_id.widget import WindowSetDataById
from pages.excel_write.get_row_is_column_data.widget import WindowGetRowsIsColumnData

from pages.admin.youtube.widget import WindowYoutube
from pages.admin.greed.widget import WindowCreateGreed
from pages.admin.translate_fields.widget import WindowTranslate
from pages.admin.translate_card.widget import WindowTranslateCard
from pages.admin.structure.widget import WindowStructure
from pages.admin.convertor.widget import WindowConvertor

from pages.api.api_get_idd.widget import WindowGetCardsID
from pages.api.api_get_data.widget import WindowGetCardsData
from pages.api.api_get_filters.widget import WindowGetFilterData
from pages.api.api_update_cards.widget import WindowUpdateCards

from pages.seo.speed_test.widget import WindowGetSpeedTest

from pages.image.crop.widget import WindowCropImage
from pages.image.resize.widget import WindowResizeImage
from pages.image.move.widget import WindowMoveImage


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
            self.ui.btn_split_file: WindowSplitFile(),
            self.ui.btn_read_column: WindowReadColumns(),
            self.ui.btn_check_errors: WindowCheckErrors(),
            self.ui.btn_search_text: WindowSearchText(),
            self.ui.btn_unique_values: WindowUniqueValues(),
            self.ui.menu_btn_not_use_value: WindowUnusedValues(),
            self.ui.btn_read_all_cards: WindowReadCards(),
            self.ui.btn_move_to_another: WindowMoveAnotherCell(),
            self.ui.btn_copy_to_another: WindowCopySearchCell(),
            self.ui.btn_move_search_to_cell: WindowMoveSearchCell(),
            self.ui.btn_add_text_to_start: WindowAddStartRow(),
            self.ui.btn_add_text_to_end: WindowAddEndRow(),
            self.ui.btn_add_text_to_all: WindowAddAllRow(),
            self.ui.btn_get_row_by_id: WindowGetRowsById(),
            self.ui.btn_set_data_by_id: WindowSetDataById(),
            self.ui.btn_get_row_is_column_data: WindowGetRowsIsColumnData(),
            self.ui.menu_btn_youtube: WindowYoutube(),
            self.ui.menu_btn_create_greed: WindowCreateGreed(),
            self.ui.menu_btn_translate_attr: WindowTranslate(),
            self.ui.menu_btn_translate_card: WindowTranslateCard(),
            self.ui.menu_btn_structure: WindowStructure(),
            self.ui.btn_convertor: WindowConvertor(),
            self.ui.api_get_idd: WindowGetCardsID(),
            self.ui.api_get_all: WindowGetCardsData(),
            self.ui.api_get_filters: WindowGetFilterData(),
            self.ui.api_update_cards: WindowUpdateCards(),
            self.ui.btn_speed_test: WindowGetSpeedTest(),
            self.ui.crop_space: WindowCropImage(),
            self.ui.resize_image: WindowResizeImage(),
            self.ui.collect_one_folder: WindowMoveImage()
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
        for _window in [
            self.menu_btn_windows[self.ui.btn_read_column],
            self.menu_btn_windows[self.ui.btn_check_errors],
            self.menu_btn_windows[self.ui.btn_search_text],
            self.menu_btn_windows[self.ui.btn_unique_values],
            self.menu_btn_windows[self.ui.menu_btn_not_use_value]
        ]:
            _window.receive_object_document(document)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
