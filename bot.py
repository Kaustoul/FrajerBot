import requests
import os
import shutil

from mcrcon import MCRcon
from constants import SONGS_CONTENT_PATH, SONGS_COVERS_PATH, OUT_PATH, OUT_TMP_PATH, SERVER_RCON_PORT, SERVER_RCON_PWD, DATAPACK_NAME, JAVA_PACK_OUT_PATH, SERVER_DATAPACK_NAME
from songs_manager import load_song_data, save_song_data, gen_songs_pack, merge_songs, prepare_out_folder, gen_packs, run_converter
from items_manager import update_geyser_mappings, move_geyser_pack
from server import copy_to_server, sha1_checksum
import interactions

bot = interactions.Client(token="MTIyNzMzNjk1ODc4Mzc4NzE1MA.GsZzlO.c6lJ3Xs_wvQpHjAerpVFwn_gqE1stYpfwbSFHs")

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
    song_path = os.path.join(SONGS_CONTENT_PATH, song_filename)
    cover_path = os.path.join(SONGS_COVERS_PATH, disc_texture_filename)
    
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


@bot.command(
    name="updaterp",
    description="Upload a new Resource Pack version to the server",
    scope=586545423632564234,  # Replace YOUR_GUILD_ID with your guild's ID
    options=[]
)
async def updaterp(ctx: interactions.CommandContext):
    await ctx.send("Started")
    os.makedirs(OUT_PATH, exist_ok=True)  
    shutil.rmtree(OUT_PATH, ignore_errors=True)
    os.makedirs(OUT_PATH, exist_ok=True)    
    os.makedirs(OUT_TMP_PATH, exist_ok=True)  

    print("Starting")
    prepare_out_folder()
    print("Generating songs pack")
    gen_songs_pack()
    print("Songs Generated")
    print("Merging songs pack inta main Java resource pack")
    merge_songs()
    print("Merging done")
    print("Packing resource packs")
    gen_packs()
    print("done")
    run_converter()

    update_geyser_mappings()
    move_geyser_pack()
    copy_to_server()

    with MCRcon("46.36.41.49", SERVER_RCON_PWD, SERVER_RCON_PORT) as client:
        response = client.command(f'datapack disable "file/{SERVER_DATAPACK_NAME}"')
        print("Response:", response)

        response = client.command(f'datapack enable "file/{SERVER_DATAPACK_NAME}"')
        print("Response:", response)

        response = client.command(f'rphash {sha1_checksum(JAVA_PACK_OUT_PATH)}')
        print("Response:", response)

        response = client.command('tellraw @a {"text":"ResourcePack reloaded! Relog to enjoy the new features!\\n(Bedrock user will not see new items until server restart)","color":"yellow"}')
        print("Response:", response)

    await ctx.send("Done")

if __name__ == "__main__":
    print("FrajerBot started!")
    bot.start()
