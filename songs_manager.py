import os
import json
import shutil
import subprocess
import asyncio

from constants import SONGS_COVERS_PATH, SONGS_CONTENT_PATH, ENTRY_LIST_JSON_PATH, SONGS_DATA_JSON_PATH, \
      JAVA_PACK_PATH, JAVA_PACK_NAME, BEDROCK_PACK_PATH, BEDROCK_PACK_NAME, OUT_PATH, OUT_TMP_PATH, \
      BEDROCK_PACK_OUT_PATH, JAVA_PACK_OUT_PATH, JAVA_PACK_ROOT
from merge_songs import songs_pack_copy_to_java, convert_sounds_2_bedrock, copy_records_2_bedrock
from zip import pack_folder
from response_wrapper import ResponseWrapper

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "infinite-music-discs-sessions"))
import src.generator.factory as generator_factory
from src.definitions import DiscListContents, DiscListEntryContents

def generate_song_data():
    song_data = {}
    song_files = os.listdir(SONGS_CONTENT_PATH)
    cover_files = os.listdir(SONGS_COVERS_PATH)
    cover_name = None
    cover_ext = None
    for i, song_file in enumerate(song_files):
        song_name, _ = os.path.splitext(song_file)
        for cover_file in cover_files:
            cover_name, cover_ext = os.path.splitext(cover_file)

            if cover_name.startswith("music_disc_"):
                cf = cover_file
                cover_files.remove(cover_file)
                cover_name = cover_name[len("music_disc_"):]
                new_path = os.path.join(SONGS_COVERS_PATH, cover_name + cover_ext)
                os.rename(os.path.join(SONGS_COVERS_PATH, cover_file), new_path)
                cover_files.append(new_path)

            if cover_name == song_name:
                cover_files.remove(cover_file)
                break

        song_data[i] = {
            "disc_give_name": song_name,
            "song_file": os.path.join(SONGS_CONTENT_PATH, song_file),
            "disc_texture_file": os.path.join(SONGS_COVERS_PATH, cover_name + cover_ext)
        }

    return song_data

def add_titles(songs_data):
    with open(ENTRY_LIST_JSON_PATH, "r") as f:
        input_data =  json.load(f)

        for song in input_data:
            if "internal_name" in song and "title" in song:
                int = song["internal_name"]
                title = song["title"]

                for data in songs_data.values():

                    if data["disc_give_name"] == int:
                        data["title"] = title
                        break

def save_song_data(song_data):
    with open(SONGS_DATA_JSON_PATH, "w") as f:
        json.dump(song_data, f, indent=4)

def load_song_data():
    if os.path.exists(SONGS_DATA_JSON_PATH):
        with open(SONGS_DATA_JSON_PATH, "r") as f:
            return json.load(f)
    else:
        return {}

def create_entry_list(song_data):
    entry_list = []

    for key, value in song_data.items():
        entry = {
            "texture_file": os.path.join(os.path.dirname(__file__), value["disc_texture_file"]),
            "track_file": os.path.join(os.path.dirname(__file__),  value["song_file"]),
            "title": value["title"],
            "internal_name": value["disc_give_name"],
            "custom_model_data": int(key),  # Assuming the key is the custom_model_data value
            "length": 0  # You might want to update this with the actual length of the song
        }
        entry_list.append(entry)

    # with open(INPUT_JSON_FILE, "w") as f:
    #     json.dump(entry_list, f, indent=4)
    return entry_list

def disck_list_contents_from_json(entry_list):
    disk_list = DiscListContents()
    for data in entry_list:
        entry_contents = DiscListEntryContents(
            texture_file=data["texture_file"], 
            track_file=data["track_file"], 
            title=data["title"], 
            internal_name=data["internal_name"], 
            length=data["length"], 
            custom_model_data=data["custom_model_data"]
        )

        disk_list.entries.append(entry_contents)

    return disk_list

def gen_songs_pack():
    NAME = "infinite_music_discs"
    settings = {
        'pack': '', 
        'version': {'dp': 26, 'rp': 22},
        'name': NAME,
        'zip': False, 'mix_mono': False,
        'legacy_dp': False, 
        'par_proc': False, 
        'proc_ogg': False
    }

    with open(SONGS_DATA_JSON_PATH, "r") as f:
        song_data = json.load(f)
        entry_list = create_entry_list(song_data)
        disk_list = disck_list_contents_from_json(entry_list)

    generator = generator_factory.get(settings)
    generator.validate(disk_list, settings)
    generator.create_tmp()
    generator.convert_all_to_ogg(disk_list, settings, lambda: 1 == 1)

    for e in disk_list.entries:
        e.length = generator.get_track_length(e)

    generator.generate_datapack(disk_list, settings)
    generator.generate_resourcepack(disk_list, settings)

    generator.cleanup_tmp()
    shutil.move(f"{NAME}_dp", os.path.join(OUT_TMP_PATH, f"{NAME}_dp"))
    shutil.move(f"{NAME}_rp", os.path.join(OUT_TMP_PATH, f"{NAME}_rp"))
    print("Successfully generated datapack and resourcepack!")
    
def merge_songs():
    songs_pack_copy_to_java()
    copy_records_2_bedrock()
    convert_sounds_2_bedrock()

def prepare_out_folder():
    os.makedirs(OUT_PATH, exist_ok=True)  
    shutil.rmtree(OUT_PATH, ignore_errors=True)
    os.makedirs(OUT_PATH, exist_ok=True) 
    os.makedirs(OUT_TMP_PATH, exist_ok=True) 

def gen_packs():
    pack_folder(JAVA_PACK_ROOT, JAVA_PACK_OUT_PATH)
    pack_folder(BEDROCK_PACK_PATH, BEDROCK_PACK_OUT_PATH)

async def run_converter(res: ResponseWrapper):
    command = ["java2bedrock.sh/converter.sh", JAVA_PACK_OUT_PATH, "-w", "false", "-m", BEDROCK_PACK_OUT_PATH, "-a", "null", "-b", "null", "-f", "null", "-v", "null"]
    process = asyncio.create_subprocess_exec(command, stdout=subprocess.PIPE)

    # process = await asyncio.create_subprocess_exec(".\\test.bat", stdout=subprocess.PIPE)

    async for line in process.stdout:
        await res.desc("Converting resource pack to bedrock:\n" + line.decode('utf-8'))
