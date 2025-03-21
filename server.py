import hashlib
import shutil

from constants import DATAPACK_OUT_PATH, SERVER_DATAPACK_PATH, BEDROCK_PACK_OUT_PATH, SERVER_GEYSER_PACK_PATH, GEYSER_MAPPINGS_OUT_PATH, SERVER_GEYSER_MAPPINGS_PATH

def sha1_checksum(file_path):
    # Initialize the SHA1 hash object
    sha1 = hashlib.sha1()

    # Open the file in binary mode and read it in chunks
    with open(file_path, "rb") as file:
        while chunk := file.read(65536):  # Read in 64KB chunks
            sha1.update(chunk)

    # Get the hexadecimal representation of the digest
    checksum_hex = sha1.hexdigest()

    return checksum_hex

def copy_bedrock_resource_pack_to_server():
    shutil.copytree(BEDROCK_PACK_OUT_PATH, SERVER_GEYSER_PACK_PATH)
    print(f"Resource pack copied to server successfully!")

def copy_custom_mappings_to_server():
    shutil.copytree(GEYSER_MAPPINGS_OUT_PATH, SERVER_GEYSER_MAPPINGS_PATH)
    print(f"DataPack copied to server successfully!")

def copy_datapack_to_server():
    shutil.copytree(DATAPACK_OUT_PATH, SERVER_DATAPACK_PATH)
    print(f"DataPack copied to server successfully!")

def copy_to_server():
    copy_bedrock_resource_pack_to_server()
    copy_custom_mappings_to_server()
    copy_datapack_to_server()