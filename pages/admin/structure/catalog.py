import json
import codecs
import os
from settings import Settings


class Tools:
    #  Создаем новый шаблон словаря (для всех элементов)
    def new_dict(self, cat_dict: dict) -> dict:
        return {
            "id": cat_dict["id"],
            "pid": cat_dict["pid"],
            "parents": cat_dict["parents"],
            "uri": cat_dict["uri"],
            "ordering": cat_dict["ordering"],
            "image": cat_dict["image"],
            "created_at": cat_dict["created_at"],
            "updated_at": cat_dict["updated_at"],
            "search_ordering": cat_dict["search_ordering"],
            "name_trans": self.str_to_dict_name(cat_dict["name_trans"]),
            "children": {}
        }
    
    #  Создаем новый шаблон словаряо для бновления вложеной категории
    def update_dict(self, cat_dict: dict) -> dict:
        return {
            "pid": cat_dict["pid"],
            "parents": cat_dict["parents"],
            "uri": cat_dict["uri"],
            "ordering": cat_dict["ordering"],
            "image": cat_dict["image"],
            "created_at": cat_dict["created_at"],
            "updated_at": cat_dict["updated_at"],
            "search_ordering": cat_dict["search_ordering"],
            "name_trans": self.str_to_dict_name(cat_dict["name_trans"]),
        }
    
    #  Получаем из строки json название категории
    @staticmethod
    def str_to_dict_name(data: str) -> dict:
        # Преобразуем строку в словарь
        dictionary_data = json.loads(data)
        return {
            'ru': dictionary_data['ru'],
            'uk': dictionary_data['uk']
        }
    
    #  Получаем список последовательностей IDD категорий
    @staticmethod
    def convert_str_to_list_parent_id(patent: str) -> list:
        return patent[3:-1].split('/')
    
    #  Открываем json файл с кодировкой utf-8
    @staticmethod
    def open_json_file(filename, mode) -> object:
        return json.load(codecs.open(filename=filename, mode=mode, encoding='utf-8'))
    
    #  Записываем данные в json файл
    def save_json(self, name, data, comment = ""):
        with open(name, 'w', encoding='utf-8') as file:
            # indent=4 для красивого форматирования, можно изменить по желанию
            # ensure_ascii=False для сохранения символов в их нативной форме
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"\n[+] Save - > {name} | {comment}\n")
    

class Category(Tools):
    def __init__(self, read_folder, result_folder):
        self.format = ".json"
        self.read_folder = read_folder
        self.result_folder = result_folder
        self.files = os.listdir(self.read_folder)  # Получаем список всех файлов в директории
        self.name = f"datatable{self.format}"
        self.save_name = os.path.join(self.result_folder, f"table{self.format}")
        self.root_section = os.path.join(self.result_folder, f"root_section{self.format}")
        self.last_children = os.path.join(self.result_folder, f"last_children{self.format}")
        self.free_children = os.path.join(self.result_folder, f"free_children{self.format}")

    #  Создаем новую структуру (корневые категории)
    def create_structure(self):
        file_dir = os.path.join(self.read_folder, self.name)
        open_json = self.open_json_file(filename=file_dir, mode='r')
        categories = {}
        #  Перебираем каждый элемент в списке
        for item in open_json:
            cat = self.new_dict(item)
            categories[item["id"]] = cat
            # print(f"[ {cat['id']} ] {cat['name_trans']['ru']}")
        self.save_json(self.save_name, categories, "Новая структура")
        
    #  Создаем иерархию категорий с папки categories
    def create_structure_node(self):
        structure = self.open_json_file(filename=self.save_name, mode='r')
        # Перебираем каждый файл с категориями
        for categories in self.files:
            if categories != self.name:
                open_file = os.path.join(self.read_folder, categories)
                category_list = self.open_json_file(filename=open_file, mode='r')
                # print('---->', categories, '<-----')
                # Перебираем каждую категорию в файле
                for one_category in category_list:
                    node_path_list = self.convert_str_to_list_parent_id(one_category['parents'])
                    # print(node_path_list)
                    node = self.create_node_dict(node_path_list, one_category, structure)
                    structure.update(node)
        self.save_json(self.save_name, structure, "В структуру добавлены подкатегории")

    #  Добавляем дочернюю категорию если ее нет в структуре
    def create_node_dict(self, node_idd, category, structure):
        nested_dict = structure
        current_dict = nested_dict
        for count, idd in enumerate(node_idd):
            if not current_dict.get(idd):
                current_dict.setdefault(idd, {"id": int(idd), "children": {}})
            if count == len(node_idd) -1:
                current_dict = current_dict[idd]
                new_data = self.update_dict(category)
                current_dict.update(new_data)
            else:
                 current_dict = current_dict[idd]["children"]
        return nested_dict    

    #  Обновляем категорию 
    def update_structure_node(self):
        structure = self.open_json_file(filename=self.save_name, mode='r')
        last_children = {}
        for key, value in structure.items():
            res = self.get_child(value)
            last_children.update(res)        
        self.save_json(self.last_children, last_children, "Структура обновлена из файлов")
        # print("[+]", len(last_children), 'category')
    
    def get_child(self, dictionary):
        leaf_dicts = {}
        def traverse(node):
            if not node.get("children"):
                leaf_dicts[node.get('id')] = node
            else:
                for child in node["children"].values():
                    traverse(child)
        traverse(dictionary)
        return leaf_dicts
    
    #  Получаем все корневые категории
    def get_root_section(self):
        structure = self.open_json_file(filename=self.save_name, mode='r')
        root_section = {}
        for section in structure:
            cat = {}
            cat['id'] = structure[section]['id'] 
            cat["name"] = structure[section]['name_trans']['ru']
            cat['uri'] = structure[section]['uri']
            root_section[structure[section]['id'] ] = cat
        self.save_json(self.root_section, root_section, "Главные категории")

    #  получаем список названий всех категорий 
    def get_list_name_node(self):
        structure = self.open_json_file(filename=self.last_children, mode='r')
        free_children = []
        for section in structure:
            free_children.append(structure[section]['name_trans']['ru'])
            free_children.append(structure[section]['name_trans']['uk'])
        self.save_json(self.free_children, free_children, "Получаем категории на выведение")
        # print("[+] read", len(free_children), 'category')
        return free_children
    
    def run_create_category(self):
        #  создаем структуру - корневые категории
        self.create_structure()
        
        #  добавляем все категории в структуру
        self.create_structure_node()
        
        #  получаем корневые категории
        self.get_root_section()
        
        #  обновляем все категории в структуре
        self.update_structure_node()
        
        #  получаем список названий всех категорий 
        self.get_list_name_node()
