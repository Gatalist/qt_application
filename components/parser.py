import requests
from fake_useragent import UserAgent


class WebRequester:
    """Базовый клас получения данных с сервера"""
    timeout = 40  # мах время ожидания ответа сервера

    @staticmethod
    def get_user_agent() -> dict:
        """Получение рандомный User-Agent"""
        return {'User-Agent': UserAgent().random}
    
    @staticmethod    
    def get_headers() -> dict:
        return {
            "User-Agent": UserAgent().random,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "uk-UA,uk;q=0.9,en;q=0.8",
        }

    def request_data(self, url: str, headers: dict = None):
        """Получаем ответ от сервера"""
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True
            )

            print("response status:", response.status_code)
            print("final url:", response.url)

            response.raise_for_status()
            return response

        except requests.Timeout:
            raise TimeoutError(f"Таймаут при подключении к {url}")

        except requests.exceptions.RequestException as err:
            raise ConnectionError(f"Ошибка запроса: {err}")

    @staticmethod
    def get_response_json(response: requests.Response) -> dict:
        try:
            return response.json()
        except Exception as err:
            return {'error': "error response data"}
