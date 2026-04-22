import os.path
import re, json, codecs
import threading
import pandas
from typing import Iterator
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from settings import Settings
from .convertor import Convertor


class JsonDocument(Settings):
    _instance = None
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance
    
    def __init__(self) -> None:
        self.format_open = 'Json (*.json)'
        self.document: str | None = None # ссылка на документ json
        self.all_list_admin_value = []
    
    def load_data_from_file(self, file_name):
        self.document = file_name
        threading.Thread(target = self.get_values_from_json).start()

    def get_values_from_json(self):
        file_ = json.load(codecs.open(filename=self.document, mode='r', encoding='utf-8'))
        name_values = []
        for value in file_["data"]:
            name_values.append(value['name'])
        self.all_list_admin_value = name_values


class ExcelDocument(Settings):
    _instance = None
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance
    
    def __init__(self) -> None:
        self.format_open = 'Excel (*.xlsx);;Excel (*.xls)'
        self.document: str| None = None # ссылка на документ xlsx
        
        self.data_frame: object = None  # получаем data_frame документа в pandas
        self.work_book: object = None  # открываем документ в openpyxl
        self.list_sheet: list = []  # получаем список листов в документе
        self.work_sheet: object = None  # получаем рабочий лист в документе
        self.count_row: int | None = None  # получаем список строк в документе
        self.start_row: int = 2 # с какой строки начинать читать документ
        self.list_row: list = [] # список строк на листе
        self.list_column: list = [] # список колонок на листе
        self.list_column_letters = [] # список колонок на листе типа ['A', 'B', 'C', ...]

    def load_data_from_file(self, file_name):
        self.document = file_name
        self.work_book = load_workbook(self.document)  # открываем документ в openpyxl
        self.list_sheet = self.work_book.sheetnames # получаем список листов в документе
        self.work_sheet = self.work_book[self.list_sheet[0]]  # делаем 1 лист активным по умолчанию
        self.load_data_from_sheet(sheet_name=self.list_sheet[0])

    def load_data_from_sheet(self, sheet_name):
        self.data_frame = pandas.read_excel(self.document, sheet_name=sheet_name) # получаем data_frame документа в pandas
        self.count_row = len(self.data_frame.index) + 1 # получаем список строк в листе
        self.list_row = [string for string in range(self.start_row, self.count_row + 1)] # генерируем список строк [начало, конец]
        self.list_column = self.data_frame.columns.values.tolist() # получаем все колонки на листе
        self.list_column_letters = [get_column_letter(col_idx) for col_idx in range(1, len(self.list_column) + 1)]

    def active_list_to_write(self, sheet_name):
        self.work_sheet = self.work_book[sheet_name]  # делаем лист активным по умолчанию
        self.load_data_from_sheet(sheet_name=sheet_name)

    # возвращаем список нумерованных строк с данными в указанной ячейке
    def get_rows_from_column(self, column_name) -> list:
        data_rows = []
        start_number_string = self.start_row
        for row in self.data_frame[column_name]:
            row_to_line = []
            if type(row) == str:
                row_to_line.append(start_number_string)
                row_to_line.append(row)
                data_rows.append(row_to_line)
            start_number_string += 1
        return data_rows

    # возвращаем список нумерованных строк с данными в указанной ячейке
    def get_collect_from_column(self, column_name) -> dict:
        data_rows = {}
        start_number_string = self.start_row
        for row in self.data_frame[column_name]:
            if type(row) == str:
                data_rows[start_number_string] = row
            start_number_string += 1
        return data_rows

    # получаем объект ячейки по координатам: например 'AC4'
    def get_cell_obj(self, cell_letter, cell_number) -> object:
        call = f'{cell_letter}{cell_number}'
        return self.work_sheet[call]
    
    # сохраняем результат в ячейку
    def save_result_in_cell(self, cell_object: object, text: str) -> object:
        self.work_sheet[cell_object.coordinate] = text
        return self.work_sheet

    def get_row_data(self, number_string):
        data = []
        for cell_idx in self.list_column_letters:
            cell_data_obj = self.get_cell_obj(cell_idx, number_string)
            if cell_data_obj.value is not None:
                data.append(cell_data_obj.value)
            else:
                data.append('')
        return data

    @staticmethod
    def get_current_time():
        now = datetime.now()
        time_str = now.strftime("%H-%M-%S")
        return time_str

    def save_new_file(self, path_save: str, data: list[list]):
        # Создаём новый Excel-файл
        wb = Workbook()
        # Выбираем активный лист
        ws = wb.active
        ws.title = "Worksheet"
        file_name = f"rows_for_id-{self.get_current_time()}.xlsx"
        # Заголовки колонок
        headers = self.list_column
        print("headers:", headers)
        ws.append(headers)  # append() сразу добавляет строку

        print("data:", data)
        print()
        # Записываем данные
        for row in data:
            ws.append(row)
            print("row:", row)

        # Сохраняем файл
        _path_save = os.path.join(path_save, file_name)
        wb.save(_path_save)
        print("file saved:", _path_save)

class ReadExcelDocument:
    symbol_arrow = '👉'
    symbol_ok = '✅'
    symbol_warning = '⚠️'
    symbol_forbidden = '⛔️'

    @staticmethod
    def split_text_to_value(text) -> str:
        string = ''
        call_data = text.split(';')
        for line in call_data:
            string += f'{line}\n'
        return string

    @staticmethod
    # возвращаем список нумерованных строк с данными в указанной ячейке
    def out_text(number_string, message) -> str:
        return f'-----[ Строка: {number_string} ]-----\n{message}\n'
    
    # Выводим данные ячейки. Аргумент "read_line" разобьет текст на строки по символу ";"
    def read_list_data_row(self, list_data: str) -> str:
        number = 0
        if len(list_data) > 0:
            for number_string, text in list_data:
                string = self.split_text_to_value(text)
                number += 1
                yield self.out_text(number_string, string)
        else:
            yield f"{self.symbol_forbidden} Колонка пустая\n"
        yield f"{self.symbol_ok} Прочитано строк {self.symbol_arrow} {number}\n\n"

    # Выводим данные ячейки. Аргумент "read_line" разобьет текст на строки по символу ";"
    def sorted_data_row(self, dict_data: dict) -> dict:
        unique_strings = {}
        for key, value in dict_data.items():
            if value not in unique_strings:
                unique_strings[value] = []
            unique_strings[value].append(key)

        return unique_strings

    # проверяем строку на первую заглавную букву
    def check_error_in_column(self, list_data) -> str:
        errors = 0
        for number_string, text in list_data:            
            string = ''
            check = False
            if text:
                for line in text.split(';'):
                    if len(line) < 1:
                        check = True
                        string += f'{self.symbol_warning};\n'
                        errors += 1
                    else:
                        if not line[0].istitle() and not line[0].isdigit():
                            check = True
                            string += f'{self.symbol_warning}{line}\n'
                            errors += 1
                        else:
                            string += f'{line}\n'
                if check:
                    yield self.out_text(number_string, string)
        if errors:
            yield f"❌ Ошибок {self.symbol_arrow} {errors}\n\n"
        else:
            yield f"{self.symbol_ok} Ошибок не обнаружено\n\n"

    # ищем фрагмент текста в ячейке
    def search_text(self, list_data, search: str):
        result = 0
        for number_string, text in list_data:
            like = False
            string = ''
            for element in text.split(';'):
                if element.lower().find(search.lower()) != -1:
                    string += f"{element}\n"
                    result += 1
                    like = True
            if like:
                yield self.out_text(number_string, string)
        yield f"{self.symbol_ok} Найдено совпадений {self.symbol_arrow} {result}"

    # ищем фрагмент текста в ячейке
    @staticmethod
    def search_text_(list_data, search: str):
        result = 0
        for text in list_data:
            like = False
            string = ''
            for element in text.split(';'):
                if element.lower().find(search.lower()) != -1:
                    string += f"{element}\n"
                    result += 1
                    like = True
            if like:
                yield string
        yield ""

    # получаем уникальные строки ячейки
    def get_unique_strings(self, list_data):
        unique_elem = []
        for number_string, text in list_data:
            for line in text.split(';'):
                if line not in unique_elem:
                    unique_elem.append(line)
        
        for elem in unique_elem:
            if elem == "":
                yield ";\n"
            else:
                yield f"{elem}\n"
        yield f"\n{self.symbol_ok} Уникальных строк {self.symbol_arrow} {len(unique_elem)}"

    @staticmethod
    def get_unused_value_in_admin(list_data_xl, list_data_admin):
        unique_elem = []
        for number_string, text in list_data_xl:
            for line in text.split(';'):
                if line not in unique_elem:
                    unique_elem.append(line)

        unused_value_for_admin = list(filter(lambda x: x not in unique_elem, list_data_admin))
        
        for elem in unused_value_for_admin:
            if elem == "":
                yield ";\n"
            else:
                yield f"{elem}\n"
        
        yield f"\n✅ Не используемых значений -> {len(unused_value_for_admin)}"

    # Читаем все колонки каждой строки для каждой (выводим данные всей карточки)
    @staticmethod
    def read_card_all_attr(document) -> Iterator[list]:
        for number_string in document.list_row:
            data = [['number', number_string]]

            for cell_letter in document.list_column_letters:
                cell_data_obj = document.get_cell_obj(cell_letter, number_string)
                cell_id = document.list_column_letters.index(cell_letter)
                column_name = document.list_column[cell_id]
                cell_data_text = ""
                if cell_data_obj.value is not None:
                    cell_data_text = str(cell_data_obj.value)
                data.append([column_name, cell_data_text])

            yield data

class WriteExcelDocument:
    symbols_1 = [";;", ";;;", ";;;;", "; ;", ";  ;", ";   ;"]
    symbols_2 = ["  ", "   ", "    ", "\t", "\r\n", "\n", "\r"]
    convertor = Convertor()

    # делаем первую букву каждой строки заглавной
    @staticmethod
    def upper_first_letter_in_text(text: str) -> str:
        split_text = text.split(';')
        new_list = []
        for line in split_text:
            capitalized = line[0:1].upper() + line[1:]
            new_list.append(capitalized)
        return ';'.join(new_list)
    
    # заменяем символы в строке
    def replace_symbol(self, text: str) -> str:
        for symbol in self.symbols_1:
            text.replace(symbol, ';')

        for symbol in self.symbols_2:
            text.replace(symbol, ' ')

        text.strip()

        if len(text) > 0:
            if text[0] == ';':
                text = text[1:]
        if len(text) > 0:
            if text[-1] == ';':
                text = text[:-1]
        return text.strip()

    @staticmethod
    def out_text(number_string, message):
        return f'-----[ Строка: {number_string} ]-----\n{message}\n'

    @staticmethod
    def delete_symbol_enter(text):
        pattern = r'[;\n]'
        # Разделение строки по указанным разделителям
        result = re.split(pattern, text)
        # Фильтрация пустых строк из результата
        result = list(filter(None, result))
        return ";".join(result)

    # добавление фрагмента текста
    def add_text(self, document, cell_object, text: str) -> object:
        if text:
            cell_object_value = cell_object.value
            if cell_object_value is not None:
                cell_object_value = f'{cell_object_value};{text}'
            else:
                cell_object_value = text

            clear = self.delete_symbol_enter(cell_object_value)
            clear_txt = self.replace_symbol(clear)
            upper_first_letter = self.upper_first_letter_in_text(clear_txt)
            document.save_result_in_cell(cell_object, upper_first_letter)
        else:
            document.save_result_in_cell(cell_object, None)
        return document

    # добавление фрагмента текста в конец в ячейки
    @staticmethod
    def add_text_from_position(document, cell, text: str, position: str) -> object:
        if text:
            cell_object_value = cell.value
            if cell_object_value is None:
                cell_object_value = f'{text}'
            else:
                if position == 'start':
                    cell_object_value = f'{text};{cell_object_value}'

                if position == 'end':
                    cell_object_value = f'{cell_object_value};{text}'

                # if position == 'all' and cell_object_value is not None:
                #     cell_object_value = f'{text}{cell_object_value}{text}'
                
            document.save_result_in_cell(cell, cell_object_value)

        return document

    # вырезаем весь текст с одной ячейки и добавляем в другую
    def move_text_to_another_cell(self, document, cell_move: str, cell_past: str):
        result = 0
        for number_string in document.list_row:
            cell_move_obj = document.get_cell_obj(cell_move, number_string)
            print(cell_move_obj.value)
            # вырезаем данные с ячейки если она не пустая
            if cell_move_obj.value is not None:
                save_to_return_text = cell_move_obj.value
     
                # вставляем данные в другую ячейку
                cell_past_obj = document.get_cell_obj(cell_past, number_string)
                self.add_text(document, cell_past_obj, text=cell_move_obj.value)

                # очищаем ячейку откуда копируем текст
                document.save_result_in_cell(cell_move_obj, None)
                
                yield self.out_text(number_string, save_to_return_text)
                result += 1

        yield f"✅ Текст перемещен с ячеек [ {cell_move} ] в [ {cell_past} ] - {result}\n"

    # добавление фрагмента текста в ячейку
    def add_text_to_cell(self, document, cell: str, text: str, position: str):
        result = 0
        for number_string in document.list_row:
            cell_obj = document.get_cell_obj(cell, number_string)
            self.add_text_from_position(document=document, cell=cell_obj, text=text, position=position)

            yield self.out_text(number_string, text)
            result += 1

        yield f"✅ Текст добавлен в колонку [ {cell} ] - {result} \n"

    # копируем текст поиска с ячейки и добавляем в другую ячейку
    def copy_search_text_to_other_cell(self, document, cell_move: str, cell_past: str, search: str):
        result = 0
        list_search_text_lower = [word.lower() for word in search.split(';')]
        print("[+] SEARCH TEXT", list_search_text_lower)

        for number_string in document.list_row:
            cell_move_obj = document.get_cell_obj(cell_move, number_string)
            cell_past_obj = document.get_cell_obj(cell_past, number_string)
            
            cell_move_text = cell_move_obj.value
            cell_past_text = cell_past_obj.value
            if cell_move_text is not None:
                for search_word in list_search_text_lower:
                    if cell_move_text.lower().find(search_word) != -1:

                        # save text in current cell
                        document.save_result_in_cell(cell_move_obj, cell_move_text)

                        # добавление фрагмента текста в другую ячейку
                        if cell_past_text is not None:
                            cell_past_text = ";".join(cell_move_text)
                        else:
                            cell_past_text = cell_move_text
                        document.save_result_in_cell(cell_past_obj, cell_past_text)

                yield self.out_text(number_string, cell_past_text)
                result += 1

        yield f"✅ Изменено строк - {result} \n"

    # вырезаем весь текст с одной ячейки и добавляем в другую
    def convert_units(self, document, cell_data: str, cell_result: str, select_unit: str):
        result = 0
        for number_string in document.list_row:
            cell_data_obj = document.get_cell_obj(cell_data, number_string)

            # вырезаем данные с ячейки если она не пустая
            if cell_data_obj.value is not None:
                current_text = cell_data_obj.value
                print("---", number_string, "---")
                print("current_text:", current_text)
                convert_text = self.convertor.convert(text=current_text, select_unit=select_unit)
                cell_result_obj = document.get_cell_obj(cell_result, number_string)
                print("convert_text:", convert_text)
                print("---")
                # очищаем ячейку откуда копируем текст
                document.save_result_in_cell(cell_data_obj, current_text)
                document.save_result_in_cell(cell_result_obj, convert_text)

                # yield self.out_text(number_string, save_data_text)
                yield [str(number_string), current_text, convert_text]
                result += 1

    # вырезаем весь текст с одной ячейки и добавляем в другую
    @staticmethod
    def copy_row_by_id(document, cell_id: str, list_id: list, path_save: str):
        data = []
        for number_string in document.list_row:
            cell_data_obj = document.get_cell_obj(cell_id, number_string)

            # вырезаем данные с ячейки если она не пустая
            if cell_data_obj.value is not None:
                current_text = str(cell_data_obj.value)
                if current_text in list_id:
                    data.append(document.get_row_data(number_string=number_string))
                    yield [str(number_string), str(current_text)]

        document.save_new_file(path_save, data)

    def add_data_by_id(self, document, cell_id_card: str, cell_idd_add_text: str, text: str, list_id: list):
        for number_string in document.list_row:
            cell_obj_card = document.get_cell_obj(cell_letter=cell_id_card, cell_number=number_string)
            if str(cell_obj_card.value) in list_id:
                cell_obj = document.get_cell_obj(cell_letter=cell_idd_add_text, cell_number=number_string)
                self.add_text_from_position(document=document, cell=cell_obj, text=text, position='end')
                yield f"{number_string}: {text}"

    # получаем карточки по колонке если в ней есть данные
    @staticmethod
    def copy_row_is_column_data(document, cell_id: str, path_save: str):
        data = []
        for number_string in document.list_row:
            cell_data_obj = document.get_cell_obj(cell_id, number_string)
            if cell_data_obj.value is not None:
                data.append(document.get_row_data(number_string=number_string))
                yield f"{number_string}"

        document.save_new_file(path_save, data)
