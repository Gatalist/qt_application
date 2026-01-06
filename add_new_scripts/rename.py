import os
import shutil


root_folder = input("🔹 Корневая папка с картинками: ")
output_folder = input("🔹 Куда сохранять: ")

os.makedirs(output_folder, exist_ok=True)

for root, _, files in os.walk(root_folder):
    # пропускаем сам output_folder, чтобы не зациклиться
    if os.path.abspath(root) == os.path.abspath(output_folder):
        continue

    # берём имя текущей папки
    folder_name = os.path.basename(root)
    # фильтруем только картинки
    images = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

    for i, img_name in enumerate(images, start=1):
        src_path = os.path.join(root, img_name)

        # если несколько картинок, добавляем _1, _2...
        if len(images) > 1:
            new_name = f"{folder_name}_{i}{os.path.splitext(img_name)[1]}"
        else:
            new_name = f"{folder_name}{os.path.splitext(img_name)[1]}"

        dst_path = os.path.join(output_folder, new_name)

        # если уже есть файл с таким именем – добавляем счётчик
        counter = 1
        while os.path.exists(dst_path):
            name, ext = os.path.splitext(new_name)
            dst_path = os.path.join(output_folder, f"{name}_{counter}{ext}")
            counter += 1

        shutil.move(src_path, dst_path)  # переносим файл
        print(f"✅ {src_path} → {dst_path}")
