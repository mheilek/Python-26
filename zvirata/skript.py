
import os
import shutil

# Hlavní složka, ve které jsou všechny podsložky
SOURCE_FOLDER = r"./test_set_animals/parrot"

# Cílová složka, kam se dají všechny obrázky
DEST_FOLDER = r"./test_set_animals/parrot2"

# Povolené formáty obrázků
IMAGE_EXTENSIONS = (
    ".jpg", ".jpeg", ".png", ".bmp",
    ".gif", ".webp", ".tiff"
)

os.makedirs(DEST_FOLDER, exist_ok=True)

count = 0

for root, dirs, files in os.walk(SOURCE_FOLDER):
    for file in files:
        if file.lower().endswith(IMAGE_EXTENSIONS):

            source_path = os.path.join(root, file)

            # Název nadřazené složky + původní název souboru
            folder_name = os.path.basename(root)
            new_name = f"{folder_name}_{file}"

            destination_path = os.path.join(DEST_FOLDER, new_name)

            # Kopírování obrázku
            shutil.copy2(source_path, destination_path)

            count += 1

print(f"Hotovo! Zkopírováno {count} obrázků do složky FOCE.")
