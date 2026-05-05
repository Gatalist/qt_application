from PyQt5.QtCore import QThread, pyqtSignal

class UniversalWorker(QThread):
    """
    Универсальный воркер для выполнения любой функции в отдельном потоке.
    """
    finished = pyqtSignal(list)  # Передает результат выполнения функции
    error = pyqtSignal(str)      # Передает текст ошибки

    def __init__(self, fn, **kwargs):
        super().__init__()
        self.fn = fn
        self.kwargs = kwargs

    def run(self):
        try:
            # Выполняем переданную функцию с любыми аргументами
            result = self.fn(**self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
