import json, os
from .parser import Parser, Config



# получение данных с сервера по ссылке (и API-key если нужен)
class CitrusApi(Config, Parser):
    foldef_save = 'result'
    base_citrus_api_url = 'https://api.ctrs.com.ua/router?with_meta=1&l=uk&url='
    def parse_category_card(self, category_url, page_ctart, page_end, name_save=None):
        card_list = []
        for page in range(page_ctart, page_end + 1):
            url = f'{self.base_citrus_api_url}/{category_url}/page_{page}/'
            print(url)

            page_data = self.request_data(url)

            data = page_data["data"]
            facetObject = data["facetObject"]
            items = facetObject["items"]

            card_list.extend(items)
        
        if name_save:
            file_path = os.path.join(self.path_save, name_save)
            self.save_json(file_path, card_list)
        return card_list

    def parse_card(self, url):
        new_url = f'{self.base_citrus_api_url}{url}'
        print(new_url)
        page_data = self.request_data(new_url)
        idd = page_data["data"]["idd"]
        data = f"{idd}\n"
        return data

    def get_data_card(self, data, name_save, content_type=None):
        card_list_data = []
        for item in data:
            if content_type:
                if item['preview']['src'].endswith(content_type):
                    card_list_data.append({
                        "id": item['id'],
                        "url": item['url'],
                        "src": item['preview']['src']
                    })
            else:
                card_list_data.append({
                    "id": item['id'],
                    "url": item['url'],
                    "src": item['preview']['src']
                })

        if name_save:
            new_name = name_save + content_type
            file_path = os.path.join(self.path_save, new_name)
            print(file_path)
            self.save_json(file_path, card_list_data)

    # поллучаем рич контент и картинки в галерее
    def get_galery_and_description_img(self, data, name_save):
        card_list = []
        for page in data:
            url = ''
            url = f'{self.base_citrus_api_url}{page['url']}/'
            print(url)

            page_data = self.request_data(url)

            card = {}
            data = page_data["data"]
            card["idd"] = data["idd"]
            card["reviews"] = data["reviews"]
            card["images"] = data["images"]

            card_list.append(card)
        
        file_path = os.path.join(self.path_save, name_save)
        self.save_json(file_path, card_list)
        return card_list