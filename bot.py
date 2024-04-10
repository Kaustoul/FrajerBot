import requests
import os
import json
import shutil
import subprocess

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "infinite-music-discs-sessions"))
import src.generator.factory as generator_factory
from src.definitions import DiscListContents, DiscListEntryContents

from constants import JAVA_OUT_NAME, BEDROCK_OUT_NAME
from merge_songs import java_copy_records, convert_sounds_2_bedrock, copy_records_2_bedrock
from zip import pack_folder

import interactions

bot = interactions.Client(token="MTIyNzMzNjk1ODc4Mzc4NzE1MA.GX_qv9.XUJXXp1o2L6I_X_2CCz3gs9djSoCFQ15DMTON4")

SONGS_FOLDER = os.path.join("resources", "songs")
SONGS_PATH = os.path.join(SONGS_FOLDER, "songs")
COVERS_PATH = os.path.join(SONGS_FOLDER, "covers")
JAVA_PATH = "resources/javarp/assets/minecraft/sounds/records"
BEDROCK_PATH = "resources/bedrockrp/sounds/records"
SONG_DATA_FILE = os.path.join(SONGS_FOLDER, "songs_data.json")
INPUT_JSON_FILE = "resources/songs/entry_list.json"

@bot.command(
    name="addsong",
    description="Add a new song to your Minecraft group",
    scope=586545423632564234,  # Replace YOUR_GUILD_ID with your guild's ID
    options=[
        interactions.Option(
            name="disc_give_name",
            description="Internal name / ID (max 28 characters)",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="disk_ingame_name",
            description="Disk name (Artist - Song name)",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="song_file",
            description="MP3, OGG, or WAV file",
            type=interactions.OptionType.ATTACHMENT,
            required=True
        ),
        interactions.Option(
            name="disc_texture_file",
            description="PNG file with square resolution (max 512x512)",
            type=interactions.OptionType.ATTACHMENT,
            required=True
        )
    ]
)
async def addsong(ctx: interactions.CommandContext, disc_give_name: str, disk_ingame_name: str, song_file: interactions.Attachment, disc_texture_file: interactions.Attachment):
 # Get the file extensions
    song_ext = os.path.splitext(song_file.filename)[-1]
    cover_ext = os.path.splitext(disc_texture_file.filename)[-1]

    # Construct the filenames using the internal name and file extensions
    song_filename = f"{disc_give_name}{song_ext}"
    disc_texture_filename = f"{disc_give_name}{cover_ext}"

    # Save the uploaded files into the "songs" folder
    song_path = os.path.join(SONGS_PATH, song_filename)
    cover_path = os.path.join(COVERS_PATH, disc_texture_filename)
    
    # Download the song file
    song_url = song_file.url
    song_response = requests.get(song_url)
    with open(song_path, "wb") as song_output_file:
        song_output_file.write(song_response.content)

    # Download the cover file
    cover_url = disc_texture_file.url
    cover_response = requests.get(cover_url)
    with open(cover_path, "wb") as cover_output_file:
        cover_output_file.write(cover_response.content)

    # Load existing song data or create a new dictionary if it doesn't exist
    song_data = load_song_data()

    # Add the new song data to the dictionary
    song_id = len(song_data) + 1
    song_data[song_id] = {
        "disc_give_name": disc_give_name,
        "name": disk_ingame_name,
        "song_file": song_path,
        "disc_texture_file": cover_path
    }

    # Save the updated song data to the JSON file
    save_song_data(song_data)

    await ctx.send(f"Song '{disk_ingame_name}' added with CustomModelData: {song_id}")

def generate_song_data():
    song_data = {}
    song_files = os.listdir(SONGS_PATH)
    cover_files = os.listdir(COVERS_PATH)
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
                new_path = os.path.join(COVERS_PATH, cover_name + cover_ext)
                os.rename(os.path.join(COVERS_PATH, cover_file), new_path)
                cover_files.append(new_path)

            if cover_name == song_name:
                cover_files.remove(cover_file)
                break

        song_data[i] = {
            "disc_give_name": song_name,
            "song_file": os.path.join(SONGS_PATH, song_file),
            "disc_texture_file": os.path.join(COVERS_PATH, cover_name + cover_ext)
        }

    return song_data

def update_input_data(songs_data):
    with open(INPUT_JSON_FILE, "r") as f:
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
    with open(SONG_DATA_FILE, "w") as f:
        json.dump(song_data, f, indent=4)

def load_song_data():
    if os.path.exists(SONG_DATA_FILE):
        with open(SONG_DATA_FILE, "r") as f:
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
    settings = {'pack': '', 'version': {'dp': 26, 'rp': 22}, 'name': 'infinite_music_discs', 'zip': False, 'mix_mono': False, 'legacy_dp': False, 'par_proc': False, 'proc_ogg': False}
    with open(SONG_DATA_FILE, "r") as f:
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
    print("Successfully generated datapack and resourcepack!")
    
def merge_songs():
    java_copy_records()
    copy_records_2_bedrock()
    convert_sounds_2_bedrock()

def prepare_out_folder():
    os.makedirs("out/", exist_ok=True)  
    shutil.rmtree("out/", ignore_errors=True)

def gen_packs():
    pack_folder("resources/javarp", f"{JAVA_OUT_NAME}.zip")
    pack_folder("resources/bedrockrp", f"{BEDROCK_OUT_NAME}.zip")

def run_converter():
    command = ["java2bedrock.sh/converter.sh", "out/Smazakov Pack.zip", "-w", "false", "-m", "out/Bedrock Smazakov Pack.zip", "-a", "null", "-b", "null", "-f", "null", "-v", "null"]
    subprocess.run(command)

if __name__ == '__main__':
    # Create the "songs" folder if it doesn't exist
    if not os.path.exists(SONGS_FOLDER):
        os.makedirs(SONGS_FOLDER)

    # song_data = generate_song_data()
    # update_input_data(song_data)

    # with open(SONG_DATA_FILE, "w") as f:
    #     json.dump(song_data, f, indent=4)
    # bot.start()
    gen_songs_pack()
    merge_songs()
    prepare_out_folder()
    gen_packs()