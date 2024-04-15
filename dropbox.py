import os
import requests

from constants import DROPBOX_ACCESS_TOKEN

def upload_files_to_dropbox(*file_paths):
    # Define Dropbox upload session endpoint
    upload_session_start_url = "https://content.dropboxapi.com/2/files/upload_session/start"
    upload_session_append_url = "https://content.dropboxapi.com/2/files/upload_session/append_v2"
    upload_session_finish_url = "https://content.dropboxapi.com/2/files/upload_session/finish"

    # Loop through each file path and upload it to Dropbox
    for file_path in file_paths:
        # Get file name from the file path
        file_name = os.path.basename(file_path)
        
        # Get relative folder structure
        relative_folder = os.path.dirname(file_path)

        # Start upload session
        response = requests.post(
            upload_session_start_url,
            headers={
                "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
                "Content-Type": "application/octet-stream"
            }
        )

        # print(response.json())
        upload_session_id = response.json()["session_id"]

        # Read file in chunks and append to upload session
        bytesread = 0
        with open(file_path, "rb") as file:
            while True:
                chunk = file.read(4 * 1024 * 1024)  # 4 MB chunk size
                if not chunk:
                    break  # Reached end of file
                response = requests.post(
                    upload_session_append_url,
                    headers={
                        "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
                        "Content-Type": "application/octet-stream",
                        "Dropbox-API-Arg": f'{{"cursor": {{"session_id": "{upload_session_id}", "offset": {bytesread}}}, "close": false}}'
                    },
                    data=chunk
                )

                bytesread += len(chunk)
                # print(response.json())

        # Finish upload session
        response = requests.post(
            upload_session_finish_url,
            headers={
                "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
                "Content-Type": "application/octet-stream",
                "Dropbox-API-Arg": f'{{"cursor": {{"session_id": "{upload_session_id}", "offset": {bytesread}}}, "commit": {{"path": "/{relative_folder}/{file_name}", "mode": "overwrite", "autorename": false, "mute": false}}}}'
            }
        )
        # print(response.json())
        print(f"Uploaded {file_path} to Dropbox.")


def download_file_from_dropbox(dropbox_file_path, local_save_path):
    # Define Dropbox download endpoint
    download_url = "https://content.dropboxapi.com/2/files/download"

    # Send request to download file
    response = requests.post(
        download_url,
        headers={
            "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
            "Dropbox-API-Arg": f'{{"path": "{dropbox_file_path}"}}'
        }
    )

    # Check if download was successful
    if response.status_code == 200:
        # Save downloaded file
        with open(local_save_path, "wb") as f:
            f.write(response.content)
        print(f"File downloaded and saved to {local_save_path}")
    else:
        print(f"Failed to download file: {response.text}")

def delete_file_from_dropbox(dropbox_file_path):
    # Define Dropbox delete endpoint
    delete_url = "https://api.dropboxapi.com/2/files/delete_v2"

    # Send request to delete file
    response = requests.post(
        delete_url,
        headers={
            "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        },
        json={"path": dropbox_file_path}
    )

    # Check if deletion was successful
    if response.status_code == 200:
        print(f"File {dropbox_file_path} deleted successfully from Dropbox.")
    else:
        print(f"Failed to delete file: {response.text}")