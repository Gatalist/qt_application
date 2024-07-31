import requests
import json
import os


class Parser:
    # получение данных с сервера по ссылке (и API-key если нужен)
    def request_data(self, url: str) -> json:
        try:
            result = requests.get(url)
            if result.status_code == 200:
                return result.json()
            return {'error': result}
        except Exception as error:
            print(error)

    # Запись данных в файл JSON
    def save_json(self, name, data):
        with open(f'{name}.json', 'w', encoding='utf-8') as output_file:
            json.dump(data, output_file, indent=4)  # indent=4 для удобного читаемого формата
        print(f'\nSave file -> {name}')


class Config:
    # Получение текущего рабочего каталога
    current_directory = os.getcwd()

    # Получение пути к директории выше
    parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))

    root_path = 'citrus_api'
    save_folder = 'result'

    path_save = os.path.join(parent_directory, root_path, save_folder)