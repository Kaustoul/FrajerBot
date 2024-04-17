import os
import shutil
import json

from constants import JAVA_PACK_PATH, SONGS_PACK_OUT_PATH, BEDROCK_PACK_PATH, JAVA_RECKORDS_PATH, BEDROCK_RECKORDS_PATH

def songs_pack_copy_to_java():
    source_folder = os.path.join(SONGS_PACK_OUT_PATH, "assets", "minecraft")

    os.makedirs(JAVA_PACK_PATH, exist_ok=True)
    shutil.rmtree(os.path.join(JAVA_PACK_PATH, "sounds", "records"), ignore_errors=True)

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            src_path = os.path.join(root, file)
            dest_path = os.path.join(JAVA_PACK_PATH, os.path.relpath(src_path, source_folder))
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy(src_path, dest_path)

def convert_sounds_2_bedrock():
    # Paths to JSON files
    sounds_json_path = os.path.join(JAVA_PACK_PATH, "sounds.json")
    sound_definitions_json_path = os.path.join(BEDROCK_PACK_PATH, "sounds", "sound_definitions.json")

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
    os.makedirs(BEDROCK_RECKORDS_PATH, exist_ok=True)
    shutil.rmtree(BEDROCK_RECKORDS_PATH, ignore_errors=True)
    os.makedirs(BEDROCK_RECKORDS_PATH, exist_ok=True)

    # Copy files from source to destination
    for filename in os.listdir(JAVA_RECKORDS_PATH):
        src_path = os.path.join(JAVA_RECKORDS_PATH, filename)
        dest_path = os.path.join(BEDROCK_RECKORDS_PATH, filename)
        shutil.copy(src_path, dest_path)
