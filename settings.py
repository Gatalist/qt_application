import os


class Settings(object):
    # переменные названий
    WINDOW_EXPLORE_OPEN_NAME = 'Открыть файл'
    WINDOW_EXPLORE_SAVE_NAME = 'Сохранить файл'

    # переменные сообщений
    MESSAGE_FAILED_SAVE_DOCUMENT = '⛔️ Ошибка сохранения'
    MESSAGE_DOCUMENT_IS_NOT_SAVE_PATH = '⛔️ Не выбрана папка для сохранения'

    MESSAGE_DOCUMENT_IS_NOT_OPEN = '⚠️ Не открыт документ'
    MESSAGE_DOCUMENT_IS_SAVE = '💾 Сохранено\n'

    EXCEL_FORMAT_OPEN = 'Excel (*.xlsx);;Excel (*.xls)'

    ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

    COOKIES = os.path.join(ROOT_PATH, 'source', 'chrome', 'session')

    @staticmethod
    def convert_path_to_linux(window_path: str) -> str:
        return window_path.replace("\\", "/")