import os
import shutil
import tempfile
import zipfile
import json
import urllib.request

def java_copy_records():
    destination_folder = os.path.join("resources", "javarp", "assets", "minecraft")
    source_folder = os.path.join("infinite_music_discs_rp", "assets", "minecraft")

    os.makedirs(destination_folder, exist_ok=True)
    shutil.rmtree(os.path.join(destination_folder, "sounds", "records"), ignore_errors=True)

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            src_path = os.path.join(root, file)
            dest_path = os.path.join(destination_folder, os.path.relpath(src_path, source_folder))
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy(src_path, dest_path)
            print(f"Copied {src_path} to {dest_path}")

def convert_sounds_2_bedrock():
    # Paths to JSON files
    sounds_json_path = os.path.join("resources", "javarp", "assets", "minecraft", "sounds.json")
    sound_definitions_json_path = os.path.join("resources", "bedrockrp", "sounds", "sound_definitions.json")

    # Load sounds.json
    with open(sounds_json_path, 'r') as sounds_file:
        sounds_data = json.load(sounds_file)

    # Prepare data for sound_definitions.json
    sound_definitions_data = {
        "format_version": "1.14.0",
        "sound_definitions": {}
    }

    # Iterate over sounds from sounds.json and prepare data for sound_definitions.json
    for sound_name, sound_info in sounds_data.items():
        sound_definitions_data["sound_definitions"][sound_name] = {
            "category": "music",
            "sounds": [f'sounds/{sound_info["sounds"][0]["name"]}']
        }

    # Write or overwrite sound_definitions.json
    os.makedirs(os.path.dirname(sound_definitions_json_path), exist_ok=True)
    with open(sound_definitions_json_path, 'w') as sound_definitions_file:
        json.dump(sound_definitions_data, sound_definitions_file, indent=4)

def copy_records_2_bedrock():
    # Define source and destination directories
    source_dir = os.path.join("resources", "javarp", "assets", "minecraft", "sounds", "records")
    destination_dir = os.path.join("resources", "bedrockrp", "sounds", "records")

    shutil.rmtree(destination_dir, ignore_errors=True)
    # Ensure destination directory exists
    os.makedirs(destination_dir, exist_ok=True)

    # Copy files from source to destination
    for filename in os.listdir(source_dir):
        src_path = os.path.join(source_dir, filename)
        dest_path = os.path.join(destination_dir, filename)
        shutil.copy(src_path, dest_path)
        print(f"Copied {src_path} to {dest_path}")
