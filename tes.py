def generate_song_data():
    song_data = {}
    song_files = os.listdir(SONGS_PATH)
    cover_files = os.listdir(COVERS_PATH)

    # Sort song and cover files to match each other
    song_files.sort()
    cover_files.sort()

    for i, (song_file, cover_file) in enumerate(zip(song_files, cover_files), 1):
        song_name, _ = os.path.splitext(song_file)
        cover_name, _ = os.path.splitext(cover_file)
        if cover_name.startswith("music_disc_"):
            cover_name = cover_name[len("music_disc_"):]

        song_data[i] = {
            "disc_give_name": song_name,
            "song_file_java": os.path.join(SONGS_PATH, song_file),
            "song_file_bedrock": os.path.join(SONGS_PATH, song_file),
            "disc_texture_file": os.path.join(COVERS_PATH, cover_file)
        }

    return song_data