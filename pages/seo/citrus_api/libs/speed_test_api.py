import json
import os
from .parser import Parser, Config



class SpeedPageTest(Config, Parser):
    def __init__(self):
        self.base_url = 'https://www.ctrs.com.ua'  # citrus base url page
        self.api_key = 'AIzaSyBEqZT1ymNblPkgSafDsPmQr9CMhKpsTf4'  # PageSpeed API key
       
    def worker(self, open_json, test_version_page, save_name):
        # Указать путь к вашему файлу JSON
        file_path = os.path.join(self.path_save, open_json)
       
        # Открыть файл JSON и загрузить его содержимое
        with open(file_path, 'r') as read_file:
            data = json.load(read_file)

            result = []
            for page in data:
                url = page['url']
                idd = page['id']
                url_to_analyze = self.base_url + url
                
                endpoint = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url_to_analyze}&key={self.api_key}' # desctop
                if test_version_page == 'mobile':
                    endpoint += '&strategy=mobile' # mobile               
                
                # print(url_to_analyze)
                result_speed_test = self.request_data(endpoint)
                select_data = self.select_data(idd, result_speed_test)
                print(select_data)
                result.append(select_data)
            
            new_file_path = os.path.join(self.path_save, save_name)
            self.save_json(new_file_path, result)
            # return result

    # извлекаем данные с json ответа
    def select_data(self, card_id, result_speed_test):
        if result_speed_test:
            result = {}
            metrics = result_speed_test['lighthouseResult']['audits']
            
            result["id"] = card_id
            result["url"] = result_speed_test['id']
            result["first_contentful_paint"] = metrics['first-contentful-paint']['displayValue'].replace('\u00a0', ' ')
            result["largest_contentful_paint"] = metrics['largest-contentful-paint']['displayValue'].replace('\u00a0', ' ')
            result["total_blocking_time"] = metrics['total-blocking-time']['displayValue'].replace('\u00a0', ' ')
            result["cumulative_layout_shift"] = metrics['cumulative-layout-shift']['displayValue'].replace('\u00a0', ' ')
            result["speed_index"] = metrics['speed-index']['displayValue'].replace('\u00a0', ' ')
            result["performance"] = result_speed_test['lighthouseResult']['categories']['performance']['score']
            return result
        print('Bad request, not result')
