from PyQt5.QtWidgets import QTableWidget, QApplication, QGridLayout, QTableWidgetItem, QMenu, QAction
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt


class CopyableTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._auto_add_rows_enabled = False
        self._auto_add_require_all_columns = False
        self._adding_empty_row = False
        self.cellChanged.connect(self._on_cell_changed)

    def enable_auto_add_rows(self, require_all_columns=False, add_initial_empty_row=True):
        """
        Включает автоматическое добавление строк.

        require_all_columns:
            False - строка считается заполненной, если заполнена хотя бы одна ячейка.
            True  - строка считается заполненной, только если заполнены все ячейки.

        add_initial_empty_row:
            True - если таблица пустая, сразу добавить одну пустую строку.
        """
        self._auto_add_rows_enabled = True
        self._auto_add_require_all_columns = require_all_columns

        if self.rowCount() == 0:
            if add_initial_empty_row:
                self.insertRow(0)
        else:
            last_row = self.rowCount() - 1
            if self._is_row_filled(last_row):
                self._append_empty_row()

    def disable_auto_add_rows(self):
        self._auto_add_rows_enabled = False

    def _on_cell_changed(self, row, column):
        if not self._auto_add_rows_enabled:
            return

        if self._adding_empty_row:
            return

        if self.rowCount() == 0:
            return

        # Реагируем только на последнюю строку
        if row != self.rowCount() - 1:
            return

        if self._is_row_filled(row):
            self._append_empty_row()

    def _is_row_filled(self, row):
        if self.columnCount() == 0:
            return False

        texts = []

        for col in range(self.columnCount()):
            # Если есть скрытые колонки и их не нужно учитывать,
            # раскомментируйте строку ниже:
            # if self.isColumnHidden(col):
            #     continue

            item = self.item(row, col)

            if item is not None:
                text = item.text().strip()
            else:
                text = ""

            texts.append(text)

        if not texts:
            return False

        if self._auto_add_require_all_columns:
            return all(texts)

        return any(texts)

    def _append_empty_row(self):
        self._adding_empty_row = True

        try:
            self.insertRow(self.rowCount())
        finally:
            self._adding_empty_row = False

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Copy):
            self.copy_selection()
        elif event.matches(QKeySequence.Paste):
            self.paste_clipboard()
        elif event.key() == Qt.Key_Delete:
            self.clear_selected_cells()
        else:
            super().keyPressEvent(event)

    def paste_clipboard(self):
        """Вставляет данные из буфера обмена (Google Sheets, Excel и т.д.)"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if not text:
            return

        # Разбиваем текст на строки
        lines = text.split('\n')

        # Google Sheets и Excel часто добавляют пустую строку в конце при копировании.
        # Удаляем её, чтобы не плодить пустые строки в таблице.
        if lines and lines[-1].strip() == '':
            lines.pop()

        if not lines:
            return

        # Определяем, куда вставлять (начиная с текущей выделенной ячейки)
        current_item = self.currentItem()
        if current_item:
            start_row = current_item.row()
            start_col = current_item.column()
        else:
            start_row = 0
            start_col = 0

        # Блокируем сигналы и отрисовку для скорости и чтобы не срабатывало автодобавление строк
        self.blockSignals(True)
        self.setUpdatesEnabled(False)

        try:
            # Если данных больше, чем строк в таблице - расширяем таблицу
            required_rows = start_row + len(lines)
            if required_rows > self.rowCount():
                # Временно отключаем флаг автодобавления, чтобы setRowCount не конфликтовал
                auto_add_was_enabled = getattr(self, '_auto_add_rows_enabled', False)
                self._auto_add_rows_enabled = False

                self.setRowCount(required_rows)

                self._auto_add_rows_enabled = auto_add_was_enabled

            # Проходим по строкам и ячейкам
            for r_offset, line in enumerate(lines):
                row_idx = start_row + r_offset

                # Разбиваем строку по табуляции (стандарт для табличных данных)
                cells = line.split('\t')

                for c_offset, cell_text in enumerate(cells):
                    col_idx = start_col + c_offset

                    # Не выходим за пределы количества колонок таблицы
                    if col_idx >= self.columnCount():
                        break

                    item = self.item(row_idx, col_idx)
                    if item is None:
                        item = QTableWidgetItem(cell_text)
                        self.setItem(row_idx, col_idx, item)
                    else:
                        item.setText(cell_text)

        finally:
            self.setUpdatesEnabled(True)
            self.blockSignals(False)

        # Если включено автодобавление строк, проверяем, не заполнилась ли последняя строка
        if getattr(self, '_auto_add_rows_enabled', False) and self.rowCount() > 0:
            last_row = self.rowCount() - 1
            if self._is_row_filled(last_row):
                self._append_empty_row()

    def set_data(self, data: list, clear_first: bool = True):
        """Программно заполняет таблицу, обходя конфликты с сигналами"""
        self.blockSignals(True)
        self.setUpdatesEnabled(False)

        try:
            if clear_first:
                self.setRowCount(0)

            start_row = self.rowCount()
            self.setRowCount(start_row + len(data))

            for row_offset, row_data in enumerate(data):
                current_row = start_row + row_offset

                for col, value in enumerate(row_data):
                    if col >= self.columnCount():
                        break

                    item = QTableWidgetItem(str(value) if value is not None else "")
                    self.setItem(current_row, col, item)

        finally:
            self.setUpdatesEnabled(True)
            self.blockSignals(False)

        if getattr(self, '_auto_add_rows_enabled', False) and self.rowCount() > 0:
            last_row = self.rowCount() - 1
            if self._is_row_filled(last_row):
                self._append_empty_row()

    def contextMenuEvent(self, event):
        """Контекстное меню: Копировать / Вставить / Очистить / Удалить строку"""
        menu = QMenu(self)

        copy_action = QAction("Копировать", self)
        paste_action = QAction("Вставить", self)
        clear_action = QAction("Очистить содержимое", self)
        delete_action = QAction("Удалить строку", self)

        # Все действия, кроме вставки, требуют выделения
        has_selection = bool(self.selectedIndexes())
        copy_action.setEnabled(has_selection)
        clear_action.setEnabled(has_selection)
        delete_action.setEnabled(has_selection)

        menu.addAction(copy_action)
        menu.addAction(paste_action)
        menu.addSeparator()
        menu.addAction(clear_action)
        menu.addAction(delete_action)

        action = menu.exec_(event.globalPos())

        if action == copy_action:
            self.copy_selection()
        elif action == paste_action:
            self.paste_clipboard()
        elif action == clear_action:
            self.clear_selected_cells()
        elif action == delete_action:
            self.delete_selected_rows()

    def clear_selected_cells(self):
        """Очищает содержимое выделенных ячеек."""
        selection = self.selectedIndexes()
        if not selection:
            return

        self.blockSignals(True)
        self.setUpdatesEnabled(False)

        try:
            for index in selection:
                item = self.item(index.row(), index.column())
                if item:
                    item.setText("")
        finally:
            self.setUpdatesEnabled(True)
            self.blockSignals(False)

    def copy_selection(self):
        selection = self.selectedIndexes()

        if not selection:
            return

        selection.sort(key=lambda x: (x.row(), x.column()))
        rows = {}
        for index in selection:
            item = self.item(index.row(), index.column())
            if item:
                rows.setdefault(index.row(), {})[index.column()] = item.text()

        copied_text = ""
        for row in sorted(rows):
            line = "\t".join(
                rows[row].get(col, "")
                for col in sorted(rows[row])
            )
            copied_text += line + "\n"

        QApplication.clipboard().setText(copied_text.strip())

    def delete_selected_rows(self):
        """Удаляет все выделенные строки."""
        # Получаем уникальные номера выделенных строк и сортируем их по убыванию
        # (удалять нужно с конца, чтобы не сбивались индексы)
        selected_rows = sorted(list(set(index.row() for index in self.selectedIndexes())), reverse=True)

        if not selected_rows:
            return

        self.blockSignals(True)
        self.setUpdatesEnabled(False)

        try:
            for row in selected_rows:
                self.removeRow(row)
        finally:
            self.setUpdatesEnabled(True)
            self.blockSignals(False)

        # Если после удаления таблица осталась пустой и включено автодобавление строк,
        # добавим одну пустую строку для удобства
        if getattr(self, '_auto_add_rows_enabled', False) and self.rowCount() == 0:
            self.insertRow(0)

    @classmethod
    def replace_table_with_copyable(cls, old_table, **options):
        """
        Публичный метод для замены обычного QTableWidget на CopyableTableWidget.
        """
        return cls.replace_table(old_table, **options)

    @classmethod
    def replace_table(
        cls,
        old_table,
        *,
        parent=None,
        object_name=None,
        row_count=None,
        column_count=None,
        headers=None,
        column_widths=None,
        selection_mode=None,
        selection_behavior=None,
        edit_triggers=None,
        alternating_row_colors=None,
        show_horizontal_header=None,
        show_vertical_header=None,
        style_sheet=None,
        copy_font=True,
        copy_size_policy=True,
        copy_minimum_size=True,
        auto_add_rows=False,
        auto_add_require_all_columns=False,
        auto_add_initial_empty_row=True,
    ):
        """
        Создаёт CopyableTableWidget и заменяет им old_table в layout.

        Параметры:
            old_table: QWidget
                Старая таблица, которую нужно заменить.
            parent: QWidget, optional
                Родитель для новой таблицы. По умолчанию берётся из old_table.
            object_name: str, optional
                objectName новой таблицы. По умолчанию копируется из old_table.
            column_count: int, optional
                Количество колонок.
            headers: list[str], optional
                Заголовки колонок.
            column_widths: list[int] | dict[int, int], optional
                Ширина колонок.
                Например:
                    [100, 200, 300]
                или:
                    {0: 100, 1: 200, 2: 300}
            selection_mode: QAbstractItemView.SelectionMode, optional
            selection_behavior: QAbstractItemView.SelectionBehavior, optional
            edit_triggers: QAbstractItemView.EditTriggers, optional
            alternating_row_colors: bool, optional
            show_horizontal_header: bool, optional
            show_vertical_header: bool, optional
            style_sheet: str, optional
            copy_font: bool
                Копировать шрифт старой таблицы.
            copy_size_policy: bool
                Копировать size policy старой таблицы.
            copy_minimum_size: bool
                Копировать минимальный размер старой таблицы.
        """

        if old_table is None:
            raise ValueError("old_table не может быть None")

        parent = parent or old_table.parentWidget()

        new_table = cls(parent)

        # Сохраняем objectName, чтобы могли работать старые стили/поиск по имени
        new_table.setObjectName(
            object_name if object_name is not None else old_table.objectName()
        )

        # Базовое копирование внешних свойств
        if copy_font:
            new_table.setFont(old_table.font())

        if copy_minimum_size:
            new_table.setMinimumSize(old_table.minimumSize())

        if copy_size_policy:
            new_table.setSizePolicy(old_table.sizePolicy())

        # Настройка колонок
        if headers is not None:
            headers = list(headers)

            if column_count is None:
                effective_column_count = len(headers)
            else:
                effective_column_count = max(column_count, len(headers))

            new_table.setColumnCount(effective_column_count)
            new_table.setHorizontalHeaderLabels(headers)

        elif column_count is not None:
            new_table.setColumnCount(column_count)

        else:
            # Если параметры не переданы — копируем колонки из старой таблицы
            old_column_count = old_table.columnCount()
            new_table.setColumnCount(old_column_count)

            old_headers = []
            for col in range(old_column_count):
                header_item = old_table.horizontalHeaderItem(col)
                old_headers.append(header_item.text() if header_item else "")

            if old_headers:
                new_table.setHorizontalHeaderLabels(old_headers)

        if row_count is not None:
            new_table.setRowCount(row_count)

        # Ширина колонок
        if column_widths is not None:
            if isinstance(column_widths, dict):
                for col, width in column_widths.items():
                    new_table.setColumnWidth(col, width)
            else:
                for col, width in enumerate(column_widths):
                    new_table.setColumnWidth(col, width)

        # Дополнительные настройки таблицы
        if selection_mode is not None:
            new_table.setSelectionMode(selection_mode)

        if selection_behavior is not None:
            new_table.setSelectionBehavior(selection_behavior)

        if edit_triggers is not None:
            new_table.setEditTriggers(edit_triggers)

        if alternating_row_colors is not None:
            new_table.setAlternatingRowColors(alternating_row_colors)

        if show_horizontal_header is not None:
            new_table.horizontalHeader().setVisible(show_horizontal_header)

        if show_vertical_header is not None:
            new_table.verticalHeader().setVisible(show_vertical_header)

        if style_sheet is not None:
            new_table.setStyleSheet(style_sheet)

        was_visible = not old_table.isHidden()

        # Ищем layout, в котором находится старая таблица
        layout = cls._find_layout_containing(old_table)

        if layout is not None:
            # Для QGridLayout дополнительно сохраняем row/column/span
            if isinstance(layout, QGridLayout):
                index = layout.indexOf(old_table)

                if index != -1:
                    row, column, row_span, column_span = layout.getItemPosition(index)

                    layout.removeWidget(old_table)
                    layout.addWidget(
                        new_table,
                        row,
                        column,
                        row_span,
                        column_span,
                    )
                else:
                    layout.addWidget(new_table)

            else:
                if layout.indexOf(old_table) != -1:
                    layout.replaceWidget(old_table, new_table)
                else:
                    layout.addWidget(new_table)

        else:
            # Fallback, если таблица вдруг не находится в layout
            new_table.setGeometry(old_table.geometry())

        new_table.setVisible(was_visible)

        # Убираем старую таблицу
        old_table.hide()
        old_table.setParent(None)
        old_table.deleteLater()

        if auto_add_rows:
            new_table.enable_auto_add_rows(
                require_all_columns=auto_add_require_all_columns,
                add_initial_empty_row=auto_add_initial_empty_row,
            )

        return new_table

    @classmethod
    def _find_layout_containing(cls, widget):
        """
        Ищет layout, в котором реально находится widget.
        """
        parent = widget.parentWidget()

        while parent is not None:
            layout = parent.layout()

            if layout is not None:
                found_layout = cls._find_layout_recursive(layout, widget)
                if found_layout is not None:
                    return found_layout

            parent = parent.parentWidget()

        return None

    @classmethod
    def _find_layout_recursive(cls, layout, widget):
        """
        Рекурсивно ищет widget внутри layout и вложенных layout.
        """
        if layout.indexOf(widget) != -1:
            return layout

        for i in range(layout.count()):
            item = layout.itemAt(i)

            if item is None:
                continue

            child_layout = item.layout()

            if child_layout is not None:
                found = cls._find_layout_recursive(child_layout, widget)
                if found is not None:
                    return found

        return None


# Заменяем tableWidget на CopyableTableWidget
# self.ui.tableWidget = CopyableTableWidget.replace_table_with_copyable(
#     self.ui.tableWidget,
#     column_count=3,
#     headers=["FilterGroup", "FilterName", "FilterURL"],
#
#     # Примеры дополнительных настроек:
#     # column_widths=[200, 250, 350],
#     # alternating_row_colors=True,
#     # show_vertical_header=False,
#     # style_sheet="QTableWidget { background: white; }",
# )