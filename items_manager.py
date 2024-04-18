import yaml
import json
import os
import shutil

from constants import SONGS_DATA_JSON_PATH, GEYSER_MAPPINGS_PATH, GEYSER_MAPPINGS_OUT_PATH, OUT_PATH, BEDROCK_PACK_OUT_PATH

def geyser_mappings_add_item_titles(mappings_data, filepath=None, data=None):
    if data is None:
       assert filepath
       with open(filepath, 'r', encoding='utf-8') as f:
        data =  yaml.safe_load(f)

    for mat in data.keys():
        for value in data[mat].values():
            custom_model_data = value["customModelData"]

            item_mappings = mappings_data[f"minecraft:{mat.lower()}"]
            for mapping in item_mappings:
                if mapping["custom_model_data"] == custom_model_data and "displayName" in value:
                    mapping["display_name"] = value["displayName"]

def geyser_mappings_add_record_titles(mappings_data):
    with open(SONGS_DATA_JSON_PATH, 'r') as f:
        data = json.load(f)

    for custom_model_data, value in data.items():
        item_mappings = mappings_data["minecraft:music_disc_11"]
        for mapping in item_mappings:
            if mapping["custom_model_data"] == custom_model_data and "title" in value:
                mapping["display_name"] = value["title"]


def update_geyser_mappings():
    with open(GEYSER_MAPPINGS_PATH, 'r') as mappings:
        mappings_json = json.load(mappings)

    mappings_data = mappings_json["items"]
    geyser_mappings_add_item_titles(mappings_data, os.path.join("resources", "custom-hats.yml"))
    geyser_mappings_add_record_titles(mappings_data)

    with open(GEYSER_MAPPINGS_OUT_PATH, 'w') as out_file:
        json.dump(mappings_json, out_file, indent=4)

def move_geyser_pack():
    shutil.move(os.path.join("target", "packaged", "geyser_resources.mcpack"), BEDROCK_PACK_OUT_PATH)
