from PyQt5.QtCore import QThread, pyqtSignal

class UniversalWorker(QThread):
    """
    Универсальный воркер для выполнения любой функции в отдельном потоке.
    """
    finished = pyqtSignal()  # Передает результат выполнения функции
    error = pyqtSignal(str)      # Передает текст ошибки

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
            self.finished.emit()  # без аргументов
        except Exception as e:
            self.error.emit(str(e))
