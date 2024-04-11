import os

OUT_PATH = "out"
OUT_TMP_PATH = os.path.join(OUT_PATH, "tmp")

SONGS_PATH = os.path.join("resources", "songs")
SONGS_CONTENT_PATH = os.path.join(SONGS_PATH, "songs")
SONGS_COVERS_PATH = os.path.join(SONGS_PATH, "covers")

JAVA_PACK_PATH = os.path.join("resources", "javarp", "assets", "minecraft", "sounds", "records")
JAVA_RECKORDS_PATH = os.path.join(JAVA_PACK_PATH, "sounds", "records")
JAVA_PACK_NAME = "Smazakov Pack"
JAVA_PACK_OUT_PATH = os.path.join(OUT_PATH, f"{JAVA_PACK_NAME}.zip")

SERVER_PATH = "var/lib/pterodactyl/6ee8f535-c065-471b-9bb9-ac3d71c9c8cb"
SERVER_GEYSER_MAPPINGS_PATH = os.path.join(SERVER_PATH, "plugins", "Geyser-Spigot" "custom_mappings", "geyser_mappings.json")
SERVER_GEYSER_PACK_PATH = os.path.join(SERVER_PATH, "plugins", "RadkuvPlugin", "data", "bedrockpack.mcpack")
SERVER_DATAPACK_PATH = os.path.join(SERVER_PATH, "world", "datapacks", "hudba")
SERVER_RCON_PORT = 25566
SERVER_RCON_PWD = "tXZrznQhwy7Wdk3m"

DATAPACK_NAME = "infinite_music_discs_dp"
DATAPACK_OUT_PATH = os.path.join(OUT_TMP_PATH, DATAPACK_NAME)
SONGS_PACK_OUT_PATH = os.path.join(OUT_TMP_PATH, "infinite_music_discs_rp")

BEDROCK_PACK_PATH = os.path.join("resources", "bedrockrp")
BEDROCK_RECKORDS_PATH = os.path.join(BEDROCK_PACK_PATH, "sounds", "records")
BEDROCK_SOUND_DEFINITIONS_PATH = os.path.join(BEDROCK_PACK_PATH, "sounds", "sound_definitions.json")
BEDROCK_PACK_NAME = "Bedrock Smazakov Pack"
BEDROCK_PACK_OUT_PATH = os.path.join(OUT_TMP_PATH, f"{BEDROCK_PACK_NAME}.zip")

SONGS_DATA_JSON_PATH = os.path.join(SONGS_PATH, "songs_data.json")
ENTRY_LIST_JSON_PATH = os.path.join(OUT_TMP_PATH, "entry_list.json")
CUSTOM_ITEMS_YML = os.path.join("resources", "custom-items.yml")

GEYSER_MAPPINGS_NAME = "geyser_mappings.json"
GEYSER_MAPPINGS_PATH = os.path.join("target", GEYSER_MAPPINGS_NAME)
GEYSER_MAPPINGS_OUT_PATH = os.path.join(OUT_PATH, GEYSER_MAPPINGS_NAME)
