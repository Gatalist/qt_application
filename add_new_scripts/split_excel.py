import pandas as pd
from pathlib import Path

# ===== НАСТРОЙКИ =====
INPUT_FILE = input("input.xlsx: ")   # исходный файл
ROWS_PER_FILE = 400         # сколько строк в одном файле
OUTPUT_DIR = input("output_dir: ") # папка для результатов
# ====================

def split_excel(
    input_file: str,
    rows_per_file: int,
    output_dir: str
):
    df = pd.read_excel(input_file)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    total_rows = len(df)
    file_count = (total_rows + rows_per_file - 1) // rows_per_file

    for i in range(file_count):
        start = i * rows_per_file
        end = start + rows_per_file

        chunk = df.iloc[start:end]

        output_file = output_dir / f"part_{i + 1:03}.xlsx"
        chunk.to_excel(output_file, index=False)

        print(f"Создан файл: {output_file} ({len(chunk)} строк)")

    print(f"\nГотово! Всего файлов: {file_count}")

if __name__ == "__main__":
    split_excel(
        INPUT_FILE,
        ROWS_PER_FILE,
        OUTPUT_DIR
    )
