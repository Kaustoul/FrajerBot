from ftplib import FTP
import yaml
from io import BytesIO

class FTPUploader:
    def __init__(self, hostname, port, username, pwd):
        self.ftp = FTP()
        self.ftp.connect(hostname, port)
        self.ftp.login(username, pwd)

    def upload(self, local_file_path, remote_file_path):
        try:
            with open(local_file_path, 'rb') as f:
                self.ftp.storbinary(f'STOR {remote_file_path}', f)
            print("File uploaded successfully via FTP.")

        except Exception as e:
            print(f"Error uploading file: {e}")

    def upload_yaml(self, output_filename, yaml_dict):
        yaml_str = yaml.dump(yaml_dict)
        yaml_bytes = yaml_str.encode('utf-8')
        self.ftp.storbinary(f'STOR {output_filename}', BytesIO(yaml_bytes))

    def close(self):
        self.ftp.quit()
