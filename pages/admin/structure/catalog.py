import json
import time
import os
from settings import Settings
from components.browser import Browser


class Category(Browser):
    def __init__(self):
        super().__init__()
        self.link_structure = "https://my.ctrs.com.ua/contento/content/catalog/categories/structure/datatable/"
        self.datatable_file = os.path.join(Settings.ROOT_PATH, "source", "datatable.json")
        self.structure = {}

    def get_structure(self, page_name: str, link: str):
        self.open_url(page_name=page_name, link=link)
        content = self.pages[page_name].content()
        return self.get_json_for_pre(content)

    def add_category_to_main(self, page_name: str, datatable: list):
        for category in datatable:
            self.structure[category["id"]] = category
            self.add_parent_category(page_name=page_name, category_id=category["id"])

    def add_parent_category(self, page_name: str, category_id: int):
        link_parent_category = f"{self.link_structure}?parent_category_id={category_id}&with_trashed=0"
        self.open_url(page_name=page_name, link=link_parent_category)
        content = self.pages[page_name].content()
        _json_content = self.get_json_for_pre(content)
        time.sleep(2)
        if _json_content:
            for child in _json_content:
                print("\n-----")
                nodes = self.get_parent_nesting(nesting=child["parents"])
                self.insert_child(root=self.structure, nodes=nodes, child=child)

                self.add_parent_category(page_name=page_name, category_id=child["id"])
                print("-----\n")
        return

    @staticmethod
    def insert_child(root: dict, nodes: list, child: dict):
        current = root
        nodes.pop()
        for node_id in nodes:
            if not current.get(node_id):
                current.setdefault(node_id, {})
            current = current[node_id]
        current[child["id"]] = child

    @staticmethod
    def get_parent_nesting(nesting: str):
        """
        nesting it's attribute 'parents': '/0/18/'
        """
        _nesting = nesting.split("/")
        nodes = [int(node) for node in _nesting if node not in ['', '0']]
        result = []

        for i, val in enumerate(nodes):
            result.append(val)
            if i != len(nodes) - 1:
                result.append("parent")
        print("nodes:", result)
        return result

    def save_structure_to_json(self):
        with open(self.datatable_file, "w", encoding="utf-8") as _file:
            json.dump(self.structure, _file, ensure_ascii=False, indent=4)

    def get_structure_from_json(self):
        with open(self.datatable_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    def get_categories_name(self, dict_data: dict, lang: str ="uk", all_cat: bool = False):
        last_children = []
        for idd, category in dict_data.items():
            res = self.get_child(dict_data=category, lang=lang, all_cat=all_cat)
            last_children.extend(res)
        return last_children

    @staticmethod
    def get_child(dict_data: dict, lang: str = 'uk', all_cat: bool = False):
        leaf_dicts = []

        def traverse(node: dict, _lang: str, _all_cat: bool):
            if not node.get("parent"):
                leaf_dicts.append(node.get("translations", {}).get("name", {}).get(_lang, ""))
            else:
                if _all_cat:
                    leaf_dicts.append(node.get("translations", {}).get("name", {}).get(_lang, ""))
                for child in node["parent"].values():
                    traverse(node=child, _lang=_lang, _all_cat=_all_cat)
        traverse(node=dict_data, _lang=lang, _all_cat=all_cat)
        return leaf_dicts
