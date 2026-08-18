import os
import shutil
from PIL import Image, ImageChops
from queue import Queue


class ImageManager:
    def __init__(self):
        self.format_allowed = ('.png', '.jpg', '.jpeg', '.jpeg', '.webp')
        self.format_forbidden = ('.psd',)

    def crop_space(self, in_path: str, padding_space: int = 10, result_queue: Queue = None):
        """
            :param in_path: "C:\Desktop\Content"
            :param padding_space: int (padding space px)
            :param result_queue: Queue для передачи результатов
        """
        output_folder = in_path + "_crop"
        os.makedirs(output_folder, exist_ok=True)  # Создаём корневую папку сразу

        for root, _, files in os.walk(in_path):
            rel_path = os.path.relpath(root, in_path)

            if rel_path == '.':
                save_dir = output_folder
            else:
                save_dir = os.path.join(output_folder, rel_path)

            os.makedirs(save_dir, exist_ok=True)

            for filename in files:
                if filename.lower().endswith(self.format_allowed):
                    src_path = os.path.join(root, filename)
                    dst_path = os.path.join(save_dir, filename)

                    try:
                        img = Image.open(src_path).convert("RGB")
                        bg = Image.new("RGB", img.size, (255, 255, 255))

                        diff = ImageChops.difference(img, bg)
                        diff = Image.eval(diff, lambda x: 255 if x > 10 else 0)
                        bbox = diff.getbbox()

                        if bbox:
                            left = max(bbox[0] - padding_space, 0)
                            upper = max(bbox[1] - padding_space, 0)
                            right = min(bbox[2] + padding_space, img.width)
                            lower = min(bbox[3] + padding_space, img.height)
                            cropped = img.crop((left, upper, right, lower))
                        else:
                            cropped = img

                        cropped.save(dst_path)
                        print(f"✅ {dst_path}")

                        image_data = {
                            "name": filename,
                            "status": "✅",
                            "path": dst_path
                        }

                        # Отправляем результат в очередь
                        if result_queue:
                            result_queue.put(image_data)

                    except Exception as e:
                        print(f"❌ Ошибка при обработке {filename}: {e}")
                        if result_queue:
                            result_queue.put({
                                "name": filename,
                                "status": "❌ Ошибка",
                                "path": dst_path
                            })

    def move_for_one_folder(self, in_path: str, result_queue: Queue = None):
        """
            :param in_path: "C:\Desktop\Content"
            :param result_queue: Queue для передачи результатов
        """
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

                base_name, ext = os.path.splitext(file)

                # Если файл с таким именем уже существует — переименуем
                if os.path.exists(new_path):
                    count = 1
                    new_name = ""
                    while os.path.exists(new_path):
                        new_name = f"{base_name}_{count}{ext}"
                        new_path = os.path.join(output_folder, new_name)
                        count += 1
                    base_name = new_name

                image_data = {
                    "name": base_name,
                    "path": new_path,
                    "status": "✅"
                }

                print("Копирую:", file_path, "→", new_path)
                shutil.copy2(file_path, new_path)

                # Отправляем результат в очередь
                if result_queue:
                    result_queue.put(image_data)

        print("\nГотово!")

    @staticmethod
    def return_text_part(text: str, split_symbol: str = "_", return_part: int = 0):
        _split = text.split(split_symbol)
        if len(_split) > 1:
            text = _split[return_part]
        return text

    def resize_image(self, in_path: str, max_width: int = 2500, quality=90, safe_format="webp", result_queue: Queue = None):
        output_folder = in_path + "_resize"
        os.makedirs(output_folder, exist_ok=True)

        for filename in os.listdir(in_path):
            if not filename.lower().endswith(self.format_allowed):
                continue

            source_path = os.path.join(in_path, filename)
            name, ext = os.path.splitext(filename)

            # Определяем целевой формат
            # Если safe_format передан, берем его, иначе оставляем старое расширение (без точки)
            target_format = safe_format.lower() if safe_format else ext.replace(".", "").lower()

            # Для корректного сохранения в Pillow (jpeg -> jpg)
            save_format = "JPEG" if target_format == "jpg" else target_format.upper()

            new_filename = f"{name}.{target_format}"
            output_path = os.path.join(output_folder, new_filename)

            image_data = {
                "name": f"{name}{ext}",
                "path": output_path
            }

            try:
                with Image.open(source_path) as img:
                    width, height = img.size
                    current_img = img

                    # 1. Делаем ресайз, если нужно
                    if width > max_width:
                        ratio = max_width / width
                        new_height = int(height * ratio)
                        current_img = img.resize((max_width, new_height), Image.LANCZOS)
                        status_msg = f"✅ {width}px → {max_width}px (resize)"
                    else:
                        status_msg = f"✖️ {width}px"

                    # 2. Обработка прозрачности перед сохранением
                    # Если сохраняем в JPEG (который не ест прозрачность), конвертируем в RGB
                    if save_format == "JPEG":
                        current_img = current_img.convert("RGB")
                    elif current_img.mode in ("RGBA", "P") and save_format == "WEBP":
                        current_img = current_img.convert("RGBA")
                    elif current_img.mode not in ("RGB", "RGBA"):
                        current_img = current_img.convert("RGB")

                    # 3. Сохранение
                    current_img.save(output_path, save_format, quality=quality)
                    image_data["status"] = f"{status_msg} ({save_format})"
                    print(status_msg)
            except Exception as e:
                image_data["status"] = "❌ Ошибка"
                print(f"{image_data['status']} при обработке {filename}: {e}")

            # Отправляем результат в очередь
            if result_queue:
                result_queue.put(image_data)
        print("\nГотово!")