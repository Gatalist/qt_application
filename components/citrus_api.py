from time import sleep
from .parser import WebRequester


class CitrusApi(WebRequester):
    def __init__(self):
        self.domain_api = "https://api.ctrs.com.ua"
        self.domain = "https://www.ctrs.com.ua"
        self.base_citrus_api_url = f'{self.domain_api}/router?with_meta=1&l=uk&url='
        self.category_cards = None
        self.cards_id = []
        self.cards_data = []
        self.category_filters = []

    def get_category_cards(self, category_slug, page_start, page_end):
        card_list = []
        count = 1
        for page in range(page_start, page_end + 1):
            url = f'{self.base_citrus_api_url}{category_slug}page_{page}/'
            print(count, url)

            page_data = self.request_data(url)
            request_status = page_data.status_code

            # print("request:", page_data)
            _json_data = self.get_response_json(page_data)
            # print("_json_data:", _json_data)
            if request_status == 200 and _json_data:
                data = _json_data.get("data")
                if data.get("status_code") == 301:
                    break
                facet_object = data.get("facetObject")
                items = facet_object.get("items")
                card_list.extend(items)
            count += 1
            sleep(1)

        self.category_cards = card_list
        return card_list

    def get_cards_id(self):
        data_list = []
        for item in self.category_cards:
            # print("\n< ----- >")
            # print("CARD:", item)
            # print("< ----- >\n")
            idd = item.get('id')
            data_list.append(idd)
        self.cards_id = data_list

    def get_cards_data(self):
        data_list = []

        for item in self.category_cards:
            card = {
                "id": item.get('id'),
                "name": item.get('name'),
                "brand": item.get('brand').get('name') if item.get('brand') else "",
                "status": item.get('status').get('description') if item.get('status') else "",
                "price": item.get('prices').get('price') if item.get('prices') else "",
                "ordering": item.get('ordering'),
                "ordering_action": item.get('ordering_action'),
                "ordering_catalog": item.get('ordering_catalog'),
                "url": self.domain + item.get('url'),
                "image": item.get('preview').get('src') if item.get('preview') else "",
            }
            data_list.append(card)

        self.cards_data = data_list

    def get_ids(self, category_slug, page_start, page_end):
        self.get_category_cards(category_slug, page_start, page_end)
        self.get_cards_id()

    def get_data(self, category_slug, page_start, page_end):
        self.get_category_cards(category_slug, page_start, page_end)
        self.get_cards_data()

    def get_filters(self, category_slug):
        url = f'{self.base_citrus_api_url}{category_slug}'
        print(url)

        page_data = self.request_data(url)
        _json_data = self.get_response_json(page_data)
        print("_json_data:", _json_data)
        if _json_data:
            data = _json_data.get("data")
            if data:
                facet_object = data.get("facetObject")
                if facet_object:
                    self.category_filters = facet_object.get("attributes", [])

        return self.category_filters
