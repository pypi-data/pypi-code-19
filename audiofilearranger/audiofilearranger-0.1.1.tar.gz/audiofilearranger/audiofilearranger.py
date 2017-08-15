import os
import shutil
import eyed3


class Afa(object):

    def create_if_not_exists_dir(self, path):
        try:
            os.stat(path)
        except OSError:
            os.mkdir(path, 777)

    def get_category(self, category, temp_dir, mp3_meta):
        if category == 1:
            return "{}/{}".format(temp_dir, mp3_meta.tag.album)
        if category == 2:
            return "{}/{}".format(temp_dir, mp3_meta.tag.artist)
        if category == 3:
            return "{}/{}".format(temp_dir, mp3_meta.tag.album_artist)

    def afa(self):
        print("Audio file categorise (.mp3 only)")
        print("---------------------------------")
        source_path = input("Enter source path: ")  # "/Volumes/M USB 32/temp_dir"  #
        destination_path = input("Enter destination path: ")  # "/Volumes/M USB 32/temp_dir"

        category = int(input("1.Album \n2.Artist \n3.Album Artist \nEnter arrange on which category?\n"))

        temp_dir = "{}".format(destination_path)

        self.create_if_not_exists_dir(temp_dir)

        formats = '.mp3' or '.mp4'
        for dir_path, dir_names, file_names in os.walk(source_path):
            if [file_formats for file_formats in file_names if formats in file_formats]:
                for filename in file_names:
                    new_f = "{}/{}".format(dir_path, filename)
                    try:
                        mp3_meta = eyed3.load(new_f)
                        album_dir = self.get_category(category, temp_dir, mp3_meta)
                        self.create_if_not_exists_dir(album_dir)
                        shutil.copy2(new_f, album_dir)
                    except Exception as e:
                        print("Error:", e)
        else:
            print("Copy completed")


#  Afa().afa()