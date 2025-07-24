import requests
from fake_useragent import UserAgent


class WebRequester:
    """Базовый клас получения данных с сервера"""
    timeout = 40  # мах время ожидания ответа сервера

    @staticmethod
    def get_user_agent() -> dict:
        """Получение рандомный User-Agent"""
        return {'User-Agent': UserAgent().random}

    def request_data(self, url: str, headers: dict = None):
        """Получаем данные с ответа сервера"""
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if hasattr(response, 'status_code'):
                if response.status_code == 200:
                    print("response status:", response.status_code)
                    return response
            print("response status:", "Bad response -_-")
            return {}

        except requests.ConnectionError as conn_err:
            raise ConnectionError(f"Ошибка подключения")

        except requests.Timeout:
            raise TimeoutError(f"Таймаут при подключении к {url}")

        except requests.exceptions.HTTPError as http_err:
            raise ConnectionError(f"HTTP ошибка")

        except requests.exceptions.RequestException as req_err:
            raise ConnectionError(f"Ошибка запроса")

    @staticmethod
    def get_response_json(response: requests.Response) -> dict:
        if response:
            return response.json()
        return {'error': "error response data"}
