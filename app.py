import sys, os

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

from UI_window import Ui_MainWindow
from settings import Settings

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
from pages.admin.setka_auto.widget import WindowCreateSetka
from pages.admin.translate_fields.widget import WindowTranslate
from pages.admin.translate_card.widget import WindowTranslateCard
from pages.admin.structure.widget import WindowStructure


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        ## ==========================================================
        ## Добавляем текущую директорию в перемую среду
        ## ==========================================================
        # ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
        sys.path.append(Settings.ROOT_PATH)  # add root path
        
        ## ==========================================================
        ## Загрузить интерфейс из ui.py файла
        ## ==========================================================
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        ## ==========================================================
        ## получаем ui кнопки
        ## ==========================================================
        # home
        self.menu_btn_open_file = self.ui.btn_open_file
        # excel read
        self.menu_btn_read_column = self.ui.btn_read_column
        self.menu_btn_check_errors = self.ui.btn_check_errors
        self.menu_btn_search_text = self.ui.btn_search_text
        self.menu_btn_unique_values = self.ui.btn_unique_values
        self.menu_btn_unused_values = self.ui.menu_btn_not_use_value
        # excel write
        self.menu_btn_remove_another = self.ui.btn_move_to_another
        self.menu_btn_move_search  = self.ui.btn_move_search_to_cell
        self.menu_btn_add_start = self.ui.btn_add_text_to_start
        self.menu_btn_add_end = self.ui.btn_add_text_to_end
        self.menu_btn_add_all = self.ui.btn_add_text_to_all
        # excel admin
        self.menu_btn_youtube = self.ui.menu_btn_youtube
        self.menu_btn_create_setka = self.ui.menu_btn_create_setka
        self.menu_btn_translate_attr = self.ui.menu_btn_translate_attr
        self.menu_btn_translate_card = self.ui.menu_btn_translate_card
        self.menu_btn_structure = self.ui.menu_btn_structure

        ## ==========================================================
        ## инициализируем ui окна
        ## ==========================================================
        self.window_open_file = WindowOpenFile()
        
        self.window_read_columns = WindowReadColumns()
        self.window_check_errors = WindowCheckErrors()
        self.window_search_text = WindowSearchText()
        self.window_unique_values = WindowUniqueValues()
        self.windows_unused_values = WindowUnusedValues()
        
        self.window_remove_to_another = WindowRemoweAnother()
        self.window_move_search_cell = WindowMoveSearchCell()
        self.window_add_start_row = WindowAddStartRow()
        self.window_add_end_row = WindowAddEndRow()
        self.window_add_all_row = WindowAddAllRow()

        self.window_youtube = WindowYoutube()
        self.window_setka = WindowCreateSetka()
        self.window_translate = WindowTranslate()
        self.window_translate_card = WindowTranslateCard()
        self.window_structure = WindowStructure()

        ## ==========================================================
        ## Создаем dict меню, присваиваем ui кнопкам наши окна
        ## ==========================================================
        self.menu_btn_windows = {
            # home
            self.menu_btn_open_file: self.window_open_file,
            # Excel read
            self.menu_btn_read_column: self.window_read_columns,
            self.menu_btn_check_errors: self.window_check_errors,
            self.menu_btn_search_text: self.window_search_text,
            self.menu_btn_unique_values: self.window_unique_values,
            self.menu_btn_unused_values: self.windows_unused_values,
            # Excel write
            self.menu_btn_remove_another: self.window_remove_to_another,
            self.menu_btn_move_search: self.window_move_search_cell,
            self.menu_btn_add_start: self.window_add_start_row,
            self.menu_btn_add_end: self.window_add_end_row,
            self.menu_btn_add_all: self.window_add_all_row,
            # Admin
            self.menu_btn_youtube: self.window_youtube,
            self.menu_btn_create_setka: self.window_setka,
            self.menu_btn_translate_attr: self.window_translate,
            self.menu_btn_translate_card: self.window_translate_card,
            self.menu_btn_structure: self.window_structure
        }

        ## ===========================================================
        ## Показываем окно при запуке приложения
        ## ===========================================================
        self.show_home_window()
         
        ## ===========================================================
        ## Подключаем signal и slot
        ## ===========================================================
        self.menu_btn_open_file.clicked.connect(self.show_selected_window)
        
        self.menu_btn_read_column.clicked.connect(self.show_selected_window)
        self.menu_btn_check_errors.clicked.connect(self.show_selected_window)
        self.menu_btn_search_text.clicked.connect(self.show_selected_window)
        self.menu_btn_unique_values.clicked.connect(self.show_selected_window)
        self.menu_btn_unused_values.clicked.connect(self.show_selected_window)
        
        self.menu_btn_remove_another.clicked.connect(self.show_selected_window)
        self.menu_btn_move_search.clicked.connect(self.show_selected_window)
        self.menu_btn_add_start.clicked.connect(self.show_selected_window)
        self.menu_btn_add_end.clicked.connect(self.show_selected_window)
        self.menu_btn_add_all.clicked.connect(self.show_selected_window)

        self.menu_btn_youtube.clicked.connect(self.show_selected_window)
        self.menu_btn_create_setka.clicked.connect(self.show_selected_window)
        self.menu_btn_translate_attr.clicked.connect(self.show_selected_window)
        self.menu_btn_translate_card.clicked.connect(self.show_selected_window)
        self.menu_btn_structure.clicked.connect(self.show_selected_window)

        self.ui.tabWidget.tabCloseRequested.connect(self.close_tab)
        self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)
        
        # Соединяем сигнал self.window_open_file с слотами для передачи в них данных
        self.window_open_file.send_object_document.connect(self.window_read_columns.receive_object_document)
        self.window_open_file.send_object_document.connect(self.window_check_errors.receive_object_document)
        self.window_open_file.send_object_document.connect(self.window_search_text.receive_object_document)
        self.window_open_file.send_object_document.connect(self.window_unique_values.receive_object_document)
        self.window_open_file.send_object_document.connect(self.windows_unused_values.receive_object_document)

    ## ===========================================================
    ## Методы главного окна
    ## ===========================================================
    def on_tab_changed(self, index):
        print(f"Active tab index: {index}")
        print(f"Active tab name: {self.ui.tabWidget.tabText(index)}")
    
    def show_home_window(self):
        result = self.open_tab_flag(self.menu_btn_open_file.text())
        self.set_btn_checked(self.menu_btn_open_file)
        if result[0]:
            self.ui.tabWidget.setCurrentIndex(result[1])
        else:
            title = self.menu_btn_open_file.text()
            curIndex = self.ui.tabWidget.addTab(self.window_open_file, title)
            self.ui.tabWidget.setCurrentIndex(curIndex)
            self.ui.tabWidget.setVisible(True)

    def show_selected_window(self):
        button = self.sender()
        result = self.open_tab_flag(button.text())
        self.set_btn_checked(button)
        if result[0]:
            self.ui.tabWidget.setCurrentIndex(result[1])
        else:
            title = button.text()
            curIndex = self.ui.tabWidget.addTab(self.menu_btn_windows[button], title)
            self.ui.tabWidget.setCurrentIndex(curIndex)
            self.ui.tabWidget.setVisible(True)

    def close_tab(self, index):
        self.ui.tabWidget.removeTab(index)
        if self.ui.tabWidget.count() == 0:
            self.ui.toolBox.setCurrentIndex(0)
            self.show_home_window()

    def open_tab_flag(self, tab):
        open_tab_count = self.ui.tabWidget.count()
        for i in range(open_tab_count):
            tab_name = self.ui.tabWidget.tabText(i)
            if tab_name == tab:
                return True, i
            else:
                continue
        return False,

    def set_btn_checked(self, btn):
        for button in self.menu_btn_windows.keys():
            if button != btn:
                button.setChecked(False)
            else:
                button.setChecked(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
