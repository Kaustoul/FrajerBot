import requests
import os

from mcrcon import MCRcon
from constants import SONGS_CONTENT_PATH, SONGS_COVERS_PATH, GUILD_ID_OBJECT, JAVA_PACK_OUT_PATH, SERVER_RCON_PORT, SERVER_RCON_PWD, SERVER_DATAPACK_NAME, BEDROCK_PACK_OUT_PATH, BEDROCK_PACK_OUT_NAME, GEYSER_MAPPINGS_OUT_PATH
from songs_manager import load_song_data, save_song_data, gen_songs_pack, merge_songs, prepare_out_folder, gen_packs, run_converter, create_custom_items_yaml
from items_manager import update_geyser_mappings, move_geyser_pack
from server import copy_to_server, sha1_checksum, copy_resource_pack_to_webserver
from response_wrapper import ResponseWrapper
from ftp import FTPUploader

import discord
from discord import app_commands

running = False
client = discord.Client(intents=discord.Intents.default())
tree = app_commands.CommandTree(client)

@tree.command(
    name="embed",
    description="Sends an embed",
    guild=GUILD_ID_OBJECT,
)
async def embed(ctx: discord.Interaction):
    res = ResponseWrapper(ctx, "Test", "Testing")
    await res.start()
    await run_converter(res)

@tree.command(
    name="addsong",
    description="Add a new song to your Minecraft group",
    guild=GUILD_ID_OBJECT,
    extras={
        "options": [
            {
                'name': "disc_id",
                'desc': "Identifikuje disc v příkazech (max 28 znaků)",
                'type': discord.AppCommandOptionType.string,
                'required': True
            },
            {
                'name': "author_and_song_name",
                'desc': "Jméno autora a skladby (Artist - Song name)",
                'type': discord.AppCommandOptionType.string,
                'required': True
            },
            {
                'name': "song_file",
                'desc': "Soubor MP3, OGG, nebo WAV",
                'type': discord.AppCommandOptionType.attachment,
                'required': True
            },
            {
                'name': "disc_texture_file",
                'desc': "Čtvercový obrázek PNG (max 512x512)",
                'type': discord.AppCommandOptionType.attachment,
                'required': True
            },
        ]
    }
)
async def addsong(ctx: discord.Interaction, disc_id: str, author_and_song_name: str, song_file: discord.Attachment, disc_texture_file: discord.Attachment):
    print("Adding a new song")
    res = ResponseWrapper(ctx, "Adding a new song", "Just started")

    await res.start()
    await res.desc("Getting filenames")
    song_ext = os.path.splitext(song_file.filename)[-1].lower()
    cover_ext = os.path.splitext(disc_texture_file.filename)[-1].lower()

    print(song_file.filename, song_ext)
    print(disc_texture_file.filename, cover_ext)
    
    if song_ext in ['.mp3', '.ogg', '.wav'] and cover_ext == ".png":
        song_filename = f"{disc_id}{song_ext}"
        song_url = song_file.url
        disc_texture_filename = f"{disc_id}{cover_ext}"
        cover_url = disc_texture_file.url
    elif cover_ext in ['.mp3', '.ogg', '.wav'] and song_ext == ".png":
        song_filename = f"{disc_id}{cover_ext}"
        song_url = disc_texture_file.url
        disc_texture_filename = f"{disc_id}{song_ext}"
        cover_url = song_file.url
    else:
        await res.title("Failed to add a new song :(")
        await res.desc("Invalid song file format. Please upload an MP3, OGG, or WAV file.")
        await res.color(discord.Color.red())
        return

    song_path = os.path.join(SONGS_CONTENT_PATH, song_filename)
    cover_path = os.path.join(SONGS_COVERS_PATH, disc_texture_filename)
    
    await res.desc("Downloading song from discord")
    song_response = requests.get(song_url)
    with open(song_path, "wb") as song_output_file:
        song_output_file.write(song_response.content)

    await res.desc("Downloading cover image from discord")
    cover_response = requests.get(cover_url)
    with open(cover_path, "wb") as cover_output_file:
        cover_output_file.write(cover_response.content)

    await res.desc("Storing data")
    song_data = load_song_data()
    song_id = len(song_data) + 1
    song_data[song_id] = {
        "disc_give_name": disc_id,
        "title": author_and_song_name,
        "song_file": song_path,
        "disc_texture_file": cover_path
    }

    await res.desc("Saving data")
    save_song_data(song_data)

    await res.title("Successfuly added a new song!")
    await res.field(f"***{author_and_song_name}***", f"\u200B\n**Item id**: {disc_id}\n**CustomModelData**: {song_id}\n\n\n*Use '/updaterp' to apply these changes to the server*")
    await res.desc("\u200B")
    await res.thumbnail(cover_url)
    await res.color(discord.Color.green())
    print("New song added")


@tree.command(
    name="updaterp",
    description="Upload a new Resource Pack version to the server",
    guild=GUILD_ID_OBJECT,  # Replace YOUR_GUILD_ID with your guild's ID
)
async def updaterp(ctx: discord.Interaction):
    res = ResponseWrapper(ctx, "Pushing the new resource pack to Minecraft server", "Starting")
    await res.start()
    global running
    if running:
        print("ALREADY RUNNING!")
        return
    
    running = True 
    await res.desc("Preparing out folder")
    prepare_out_folder()
    await res.desc("Generating records resource pack")
    gen_songs_pack()
    await res.desc("Merging records pack into the resource pack")
    merge_songs()
    await res.desc("Packing resource pack")
    gen_packs()
    await res.desc("Running the converter")
    await run_converter(res)

    await res.desc("Updating geyser item mappings")
    update_geyser_mappings()
    move_geyser_pack()

    # await res.desc("Copying files to minecraft server")
    # copy_to_server()

    yaml_dict = create_custom_items_yaml()
    await res.desc("Uploading files to minecraft server via FTP")
    ftp_path = os.path.join("minecraft", "65e9d2b921f117421c332fce", "plugins")
    ftp = FTPUploader("ftp.hostify.cz", 21, "user_kaazaki_Rasdek", "Pgi6GdLhgAzPp8Cj")
    ftp.upload(BEDROCK_PACK_OUT_PATH, os.path.join(ftp_path, "RadkuvPlugin", "data", BEDROCK_PACK_OUT_NAME))
    ftp.upload(GEYSER_MAPPINGS_OUT_PATH, os.path.join(ftp_path, "GeyserSpigot", "custom_mappings", "geyser_mappings.json"))
    ftp.upload(os.path.join("resources", "custom-hats.yml"), os.path.join(ftp_path, "RadkuvPlugin", "custom", "custom-hats.yml"))
    ftp.upload_yaml(os.path.join(ftp_path, "RadkuvPlugin", "custom", "custom-discs.json"), yaml_dict)
    ftp.close()
    await res.desc("Copying Resource pack to webserver")
    copy_resource_pack_to_webserver()

    # await res.desc("Uploading the resource pack to Dropbox")
    # upload_files_to_dropbox(JAVA_PACK_OUT_PATH)

    await res.desc("Sending the update command to the server")
    with MCRcon("armadillo.hostify.cz", SERVER_RCON_PWD, 31361) as client:
        #response = client.command(f'datapack disable "file/{SERVER_DATAPACK_NAME}"')
        #print("Response:", response)

        #response = client.command(f'datapack enable "file/{SERVER_DATAPACK_NAME}"')
        #print("Response:", response)

        response = client.command(f'newhash {sha1_checksum(JAVA_PACK_OUT_PATH)}')
        #print("Response:", response)

        response = client.command('tellraw @a {"text":"ResourcePack reloaded! Relog to enjoy the new features!\\n(Bedrock user will not see new items until server restart)","color":"yellow"}')
        #print("Response:", response)

    await res.title("Succesfully pushed a new Resource pack to the Minecraft server!")
    await res.desc("*Relog to enjoy the new features!*")
    await res.color(discord.Color.green())

    print("Done")
    running = False

@client.event
async def on_ready():
    await tree.sync(guild=GUILD_ID_OBJECT)
    print("FrajerBot started!")


if __name__ == "__main__":
    client.run("MTIyNzMzNjk1ODc4Mzc4NzE1MA.GsZzlO.c6lJ3Xs_wvQpHjAerpVFwn_gqE1stYpfwbSFHs")

