import re
import enum


class Units(str, enum.Enum):
    cm = "cm"
    # mm = "mm"
    kg = "kg"
    # g = "g"


class Convertor:

    @staticmethod
    def convert_mm_to_cm(text: str) -> str:
        """
        Конвертирует размеры в мм в см внутри строки.
        Поддерживает разделители: x, X, *, ×.
        Если размер уже в см — пропускает.
        """

        def _mm_to_cm(match):
            part = match.group(1)
            # Разделяем по любому допустимому разделителю
            parts = re.split(r'\s*[xX*×х]\s*', part)
            # Переводим мм → см, убираем лишние нули
            cm_parts = [
                str(round(float(n.replace(',', '.')) / 10, 2)).rstrip('0').rstrip('.')
                for n in parts
            ]
            return ' x '.join(cm_parts) + ' см'

        # Число (с дробной частью) и разделители, заканчивается на "мм"
        pattern = r'((?:\d+(?:[.,]\d+)?\s*(?:[xX*×х]\s*)?)+)\s*мм(?!\w)'
        return re.sub(pattern, _mm_to_cm, text)

    @staticmethod
    def convert_weight(text: str) -> str:
        """
        Конвертирует вес в тексте:
        - Если < 1 кг → г
        - Если >= 1 кг → кг
        Поддерживает разделители "," и "."
        """

        def _convert(match):
            value_str = match.group(1).replace(',', '.')
            unit = match.group(2).lower()
            value = float(value_str)

            if unit == "кг":
                if value < 1:
                    grams = int(round(value * 1000))
                    return f"{grams} г"
                else:
                    kg_str = f"{round(value, 2):.2f}".rstrip('0').rstrip('.')
                    return f"{kg_str} кг"

            elif unit == "г":
                kg_value = value / 1000
                if kg_value < 1:
                    grams = int(round(value))
                    return f"{grams} г"
                else:
                    kg_str = f"{round(kg_value, 2):.2f}".rstrip('0').rstrip('.')
                    return f"{kg_str} кг"

        pattern = r'(\d+(?:[.,]\d+)?)\s*(кг|г)\b'
        return re.sub(pattern, _convert, text, flags=re.IGNORECASE)


    def convert(self, text: str, select_unit: str):
        print("unit...", select_unit)
        if select_unit == Units.cm.value:
            print("convert to cm...")
            try:
                return self.convert_mm_to_cm(text=text)
            except ValueError:
                return text

        elif select_unit == Units.kg.value:
            try:
                return self.convert_weight(text=text)
            except ValueError:
                return text

        elif select_unit == Units.g.value:
            ...
