from time import sleep
from components.citrus_api import CitrusApi


class SpeedPageTest(CitrusApi):
    def __init__(self):
        super(SpeedPageTest, self).__init__()
        self.speed_test_api_key = 'AIzaSyCiPi6-ORKMR39smPQPGWG1XkpOW-aHWAQ'
        self.cards_speed_test = []

    def get_result_speed_test(self, version: str, cards: list[dict]):
        result = []
        for card in cards:
            url = card['url']
            idd = card['id']
            endpoint = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={self.speed_test_api_key}' # desktop
            if version == 'Mobile':
                endpoint += '&strategy=mobile' # mobile

            # print(url_to_analyze)
            result_speed_test = self.request_data(endpoint)
            _json_response = self.get_response_json(result_speed_test)
            select_data = self.select_data(idd, _json_response)
            print("speed_test:", select_data)
            result.append(select_data)
            sleep(1)
        self.cards_speed_test = result

    @staticmethod
    def select_data(card_id, result_speed_test):
        """ извлекаем данные с json ответа """
        # print("card_result_test:", result_speed_test)
        if result_speed_test:
            lighthouse_result = result_speed_test.get('lighthouseResult', {})

            if lighthouse_result:
                _replaces = '\u00a0'
                audits = lighthouse_result.get('audits', {})
                performance = lighthouse_result.get('categories', {}).get('performance', {}).get('score', '')

                first_contentful_paint = audits.get('first-contentful-paint', {}).get('displayValue', '').replace(_replaces, ' ')
                largest_contentful_paint = audits.get('largest-contentful-paint', {}).get('displayValue', '').replace(_replaces, ' ')
                total_blocking_time = audits.get('total-blocking-time', {}).get('displayValue', '').replace(_replaces, ' ')
                cumulative_layout_shift = audits.get('cumulative-layout-shift', {}).get('displayValue', '').replace(_replaces, ' ')
                speed_index = audits.get('speed-index', {}).get('displayValue', '').replace(_replaces, ' ')

                return {
                    'id': card_id,
                    'url': audits.get('id'),
                    'first_contentful_paint': first_contentful_paint,
                    'largest_contentful_paint': largest_contentful_paint,
                    'total_blocking_time': total_blocking_time,
                    'cumulative_layout_shift': cumulative_layout_shift,
                    'speed_index': speed_index,
                    'performance': performance
                }

        print('Bad request, not result')
        return {}
