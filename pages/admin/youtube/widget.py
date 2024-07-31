from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox, QTableWidgetItem
from datetime import datetime
import threading

from .UI_window import Ui_Form
from .youtube import YouTube


class WindowYoutube(QWidget):
    def __init__(self):
        super(WindowYoutube, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.youtube = YouTube()
        
        self.yt_url_video = None
        self.title_video = None

        self.table_row_index = 1

        # Устанавливаем строку директории для чтения
        self.ui.line_save.setReadOnly(True)

        # привязываем события | чтение документа
        self.ui.check_youtube_url.clicked.connect(self.get_info_video)
        self.ui.btn_select.clicked.connect(self.select_folder)
        self.ui.btn_download.clicked.connect(self.download_video)

    # получить информацию о видео
    def get_info_video(self):
        self.yt_url_video = self.ui.search_text.text()
        if self.yt_url_video:
            self.ui.plainTextEdit.appendPlainText("Загрузка информаци..")
            threading.Thread(target = self.youtube.info_video, args=(self.yt_url_video,)).start()
            self.youtube.send_video_name.connect(self.change_text_plainTextEdit)

            self.youtube.send_formats.connect(self.view_formats)
        else:
            self.message(
                title="Видео недоступно",
                text="Проверьте правильность ссылки!",
                info = "<i>Скопируйте ссылку на видео из строки браузера...</i>"
            )

    def view_formats(self, video_formats, audio_formats):
        self.render_formats(video_formats, self.ui.comboBox_video)
        self.render_formats(audio_formats, self.ui.comboBox_audio)

    def render_formats(self, formats, comboBox):
        for key_1, video_1 in formats.items():
            print(key_1, video_1)
            if key_1:
                for key_2, video_2 in formats[key_1].items():
                    print(key_2, video_2)
                    comboBox.addItem(f"{key_1} {key_2}", video_2)

    # выведем название в наш виджет
    def change_text_plainTextEdit(self, video_title):
        self.ui.plainTextEdit.clear()
        self.ui.plainTextEdit.appendPlainText(video_title)
        self.title_video = video_title

    # окно выбира folder
    def select_folder(self):
        options = QFileDialog.Options()  # Создание объекта options
        options |= QFileDialog.ShowDirsOnly  # Добавление флага ShowDirsOnly
        folder = QFileDialog.getExistingDirectory(self, "Select Directory", "", options=options)
        if folder:
            self.ui.line_save.setText(folder)
            self.youtube.set_patch(folder)
    
    # скачивание видео
    def download_video(self):
        yt_url_video = self.ui.search_text.text()
        yt_format_video_id = self.ui.comboBox_video.currentData()
        yt_format_audio_id = self.ui.comboBox_audio.currentData()

        if not yt_url_video:
            self.message(
                title="Видео недоступно",
                text="Проверьте правильность ссылки!",
                info = "<i>Скопируйте ссылку на видео из строки браузера...</i>"
            )
        if not self.youtube.path_save:
            self.message(
                title="Выберите папку",
                text="Не выбрана папка для сохранения",
                info="<i>проверьте правильно ли указана папка для сохранения видео...</i>"
            )
        else:
            print('down...')
            threading.Thread(target = self.youtube.download, args=(yt_url_video, yt_format_video_id, yt_format_audio_id)).start()
            self.youtube.send_receiv_value.connect(self.change_progress)
            # "https://www.youtube.com/watch?v=LthW2oiyzGk"
            data = [self.title_video, self.get_date_time(), self.yt_url_video]
            self.add_data_to_table(data)
    
    # Progress bar metod...
    def change_progress(self, size):
        self.ui.progressBar.setValue(size)

    # Окно сообщения об ошибке
    def message(self, title, text, info):
        dialog = QMessageBox()
        dialog.setWindowTitle(title)
        dialog.setText(text)
        dialog.setInformativeText(info)
        dialog.setStandardButtons(QMessageBox.Cancel)
        dialog.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        dialog.exec_()

    # Добавление данных в таблицу
    def add_data_to_table(self, data):
        for col_index, cell_data in enumerate(data):
            item = QTableWidgetItem(str(cell_data))
            self.ui.tableWidget.setItem(self.table_row_index, col_index, item)
        self.table_row_index += 1
    
    @staticmethod
    def get_date_time() -> str:
        # Получение текущей даты и времени
        now = datetime.now()
        # Форматирование даты и времени в строку
        current_time = now.strftime("%d-%m-%Y %H:%M:%S")
        print("Current Time:", current_time)
        return current_time