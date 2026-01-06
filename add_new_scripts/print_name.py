import os

folder = input("🔹 Корневая папка с картинками: ")
image_ext = ('.png', '.jpg', '.jpeg', '.webp')  # допустимые расширения

names = [
    os.path.splitext(f)[0]           # берём имя без расширения
    for f in os.listdir(folder)
    if f.lower().endswith(image_ext) # фильтруем только картинки
]

for name in names:
    print(name)

print(f"\nВсего найдено: {len(names)} файлов")
