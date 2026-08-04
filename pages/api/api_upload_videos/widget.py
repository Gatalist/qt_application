from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from components.copyable_table import CopyableTableWidget
from time import sleep
from urllib.parse import urlparse, parse_qs
import json
from .UI_window import Ui_Form


class ApiWorker(QObject):
    # Сигнал теперь передает список: [id, url, code, status]
    data_ready = pyqtSignal(list)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, table_data):
        super().__init__()
        self.upload_data = table_data

    @staticmethod
    def get_youtube_code(url: str) -> str:
        """Извлекает ID видео из различных форматов YouTube ссылок."""
        try:
            parsed = urlparse(url)
            if "youtu.be" in parsed.netloc:
                return parsed.path.lstrip("/")

            qs = parse_qs(parsed.query)
            return qs.get('v', [''])[0]
        except Exception:
            return ""

    def run(self):
        from components.browser import Browser

        browser_instance = Browser(visible=False)
        try:
            page_name = "upload_video"
            browser_instance.create_page(page_name)
            browser_instance.login(page_name=page_name)

            page = browser_instance.pages[page_name]

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Requested-With": "XMLHttpRequest"  # Часто требуется для AJAX API
            }

            for card_id, url in self.upload_data:
                code = self.get_youtube_code(url)

                # Формируем URL для API
                new_url = f"{browser_instance.base_url_admin}/contento/catalog/products/{card_id}/videos"

                # Данные для отправки (адаптируйте ключ "code" под требования вашего API)
                payload = {
                    "link": url,
                    "code": code
                }
                print(f"{new_url=} {payload=}")


                # [ОПЦИОНАЛЬНО] Получение CSRF токена, если API требует его
                # csrf_token = page.evaluate("() => document.querySelector('meta[name=\"csrf-token\"]')?.content || document.querySelector('input[name=\"_token\"]')?.value || ''")
                # if csrf_token:
                #     headers["X-CSRF-TOKEN"] = csrf_token

                try:
                    # Отправляем POST запрос. Playwright сам подставит куки из context!
                    response = page.request.post(
                        new_url,
                        data=json.dumps(payload),
                        headers=headers
                    )
                    print(f"{response=}")
                    status = response.status

                    # Если нужно получить ответ сервера:
                    # try:
                    #     resp_json = response.json()
                    #     print("Server response:", resp_json)
                    # except:
                    #     pass

                except Exception as req_e:
                    status = f"ReqErr: {str(req_e)}"

                # Отправляем данные в главный поток для добавления в таблицу
                self.data_ready.emit([str(card_id), url, code, str(status)])

                sleep(3)  # Задержка между запросами, чтобы не нагружать сервер

        except Exception as e:
            self.error.emit(str(e))
        finally:
            try:
                browser_instance.close()
            except Exception:
                pass
            self.finished.emit()


class WindowUploadVideo(QWidget):
    def __init__(self):
        super(WindowUploadVideo, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # Заменяем tableWidget на CopyableTableWidget
        self.ui.tableVideo = CopyableTableWidget.replace_table_with_copyable(
            self.ui.tableVideo,
            headers=["ID", "URL"],
            row_count=5,
            auto_add_rows=True,
            auto_add_require_all_columns=False,
        )

        self.ui.tableResult = CopyableTableWidget.replace_table_with_copyable(
            self.ui.tableResult,
            row_count=5,
            # auto_add_rows=True,
            # auto_add_require_all_columns=False,
        )

        self.ui.btn_request.clicked.connect(self.start_api_thread)

        # Храним ссылки на поток и воркер, чтобы их не удалил сборщик мусора
        self.thread = None
        self.worker = None

    def start_api_thread(self):
        # 1. Собираем данные из первой таблицы
        table_data = []
        for row in range(self.ui.tableVideo.rowCount()):
            item_id = self.ui.tableVideo.item(row, 0)
            item_url = self.ui.tableVideo.item(row, 1)

            card_id = item_id.text().strip() if item_id else ""
            url = item_url.text().strip() if item_url else ""

            # Пропускаем пустые строки
            if card_id and url:
                table_data.append((card_id, url))

        if not table_data:
            QMessageBox.warning(self, "Нет данных", "Заполните ID и URL в первой таблице.")
            return

        # 2. Очищаем таблицу результатов перед стартом
        self.ui.tableResult.set_data([], clear_first=True)

        # 3. Блокируем кнопку
        self.ui.btn_request.setEnabled(False)

        # 4. Создаем поток и воркер
        self.thread = QThread()
        self.worker = ApiWorker(table_data)
        self.worker.moveToThread(self.thread)

        # 5. Подключаем сигналы
        self.thread.started.connect(self.worker.run)
        self.worker.data_ready.connect(self.add_data_to_result_table)
        self.worker.error.connect(self.handle_api_error)

        # 6. Правильное завершение
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(lambda: self.ui.btn_request.setEnabled(True))

        self.thread.start()

    def add_data_to_result_table(self, row_data):
        """
        Принимает список [id, url, code, status] и добавляет строку в таблицу результатов.
        Использование set_data с clear_first=False автоматически обходит проблемы с сигналами.
        """
        self.ui.tableResult.set_data([row_data], clear_first=False)

    def handle_api_error(self, err):
        self.ui.btn_request.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Критическая ошибка потока:\n{err}")
