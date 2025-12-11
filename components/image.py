import os
import shutil
from PIL import Image, ImageChops


class ImageManager:
    def __init__(self):
        self.format_allowed = ('.png', '.jpg', '.jpeg', '.webp')
        self.format_forbidden = ('.psd',)
        self.crop_result = []
        self.resize_result = []
        self.move_result = []

    def crop_space(self, in_path: str, padding_space: int = 10):
        """
            :param in_path: "C:\Desktop\Content"
            :param padding_space: int (padding space px)
        """
        self.crop_result = []
        output_folder = in_path + "_crop"

        for root, _, files in os.walk(in_path):
            rel_path = os.path.relpath(root, in_path)
            save_dir = os.path.join(output_folder, rel_path)
            os.makedirs(save_dir, exist_ok=True)

            for filename in files:
                if filename.lower().endswith(self.format_allowed):
                    src_path = os.path.join(root, filename)
                    dst_path = os.path.join(save_dir, filename)

                    img = Image.open(src_path).convert("RGB")
                    bg = Image.new("RGB", img.size, (255, 255, 255))

                    diff = ImageChops.difference(img, bg)
                    diff = Image.eval(diff, lambda x: 255 if x > 10 else 0)  # маска отличий
                    bbox = diff.getbbox()

                    if bbox:
                        left   = max(bbox[0] - padding_space, 0)
                        upper  = max(bbox[1] - padding_space, 0)
                        right  = min(bbox[2] + padding_space, img.width)
                        lower  = min(bbox[3] + padding_space, img.height)
                        cropped = img.crop((left, upper, right, lower))
                    else:
                        cropped = img  # если не нашли содержимого, оставляем как есть

                    cropped.save(dst_path)
                    print(f"✅ {dst_path}")
                    image_data = {
                        "name": filename,
                        "status": "✅",
                        "path": dst_path
                    }
                    self.crop_result.append(image_data)

    def move_for_one_folder(self, in_path: str):
        """
            :param in_path: "C:\Desktop\Content"
        """
        self.move_result = []
        output_folder = in_path + "_new"

        # Создаём новую папку, если её нет
        os.makedirs(output_folder, exist_ok=True)

        for root, dirs, files in os.walk(in_path):
            for file in files:
                file_path = os.path.join(root, file)

                if file.lower().endswith(self.format_forbidden):
                    continue

                # Копируем остальные файлы
                new_path = os.path.join(output_folder, file)

                # Если файл с таким именем уже существует — переименуем
                if os.path.exists(new_path):
                    base, ext = os.path.splitext(file)
                    count = 1
                    while os.path.exists(new_path):
                        new_name = f"{base}_{count}{ext}"
                        new_path = os.path.join(output_folder, new_name)
                        count += 1

                        self.move_result.append({
                            "name": new_name,
                            "path": new_path,
                            "status": "→"
                        })
                print("Копирую:", file_path, "→", new_path)
                shutil.copy2(file_path, new_path)

        print("\nГотово!")

    def resize_image(self, in_path: str, max_width: int = 2500):
        """
            :param in_path: "C:\Desktop\Content"
            :param max_width: "max width image. If size > converting on max_width if < be default"
        """
        self.resize_result = []
        output_folder = in_path + "_resize"
        os.makedirs(output_folder, exist_ok=True)

        for filename in os.listdir(in_path):
            if not filename.lower().endswith(self.format_allowed):
                continue

            source_path = os.path.join(in_path, filename)
            output_path = os.path.join(output_folder, filename)

            image_data = {
                "name": filename,
                "path": output_path
            }

            with Image.open(source_path) as img:
                width, height = img.size

                if width > max_width:
                    # вычисляем новую высоту с сохранением пропорций
                    ratio = max_width / width
                    new_height = int(height * ratio)

                    # уменьшаем изображение
                    resized = img.resize((max_width, new_height), Image.LANCZOS)

                    # сохраняем уменьшенное
                    resized.save(output_path)
                    print(f"Изменено и сохранено: {filename} ({width}px → {max_width}px)")
                    image_data["status"] = f"✅ {width}px → {max_width}px"
                else:
                    # просто копируем, если изменение не требуется
                    shutil.copy2(source_path, output_path)
                    print(f"Без изменений, скопировано: {filename} ({width}px)")
                    image_data["status"] = f"✖️ {width}px"

                self.resize_result.append(image_data)