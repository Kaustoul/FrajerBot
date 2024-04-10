import os
import zipfile

from constants import OUT_FOLDER


def zip_folder(folder_path, zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, folder_path)
                zipf.write(abs_path, arcname=rel_path)

def pack_folder(source_folder_path, out_name):
    zip_file_path = os.path.join(OUT_FOLDER, out_name)
    os.makedirs(OUT_FOLDER, exist_ok=True)
    zip_folder(source_folder_path, zip_file_path)
    print(f"Contents of {source_folder_path} zipped to {zip_file_path}")