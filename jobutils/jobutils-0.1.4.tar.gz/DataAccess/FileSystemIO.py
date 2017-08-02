#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import shutil
from shutil import copyfile

import pandas as pd

from Utils import Constants

__author__ = "laurynas@joberate.com"


class FileSystemIO(object):
    """
    Defines operations regarding data IO operations in local FileSystem
    """
    def __init__(self):

        self.const = Constants.Constants()

    def check_and_create_path(self, path):
        """
        Checks if the path exists in the FileSystem
        :param path: file path
        :return: Creates required folders in case if directories do not exist
        """
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

    def file_exists(self, file_path):
        """
        Checks if the file path exists
        :param file_path: string value indicating file path
        :return: True if file exists
        """
        return os.path.isfile(file_path)

    def directory_exists(self, dir_path):
        """
        Checks if the directory exist
        :param dir_path: string value indicating directory path
        :return: True if directory exist
        """
        return os.path.isdir(os.path.dirname(dir_path))

    def read_json(self, file_path):
        """
        Reads Json object from given file path
        :param file_path: json path
        :return: Json object
        """
        try:
            with open(file_path) as json_file:
                content = json_file.read()
                json_data = json.loads(content, encoding=self.const.ENCODING_UTF8)

            return json_data

        except Exception as e:
            print("Error while reading json %s" % file_path)
            print(e)
            return {}

    def read_csv(self, path, parse_dates=False, header=0, low_memory=False, sep=',', encoding='utf-8', dtype='unicode'):
        """
        :param header: list of strings representing table header
        :param path: csv path
        :param parse_dates: logical indicator whether date columns should be parse to date class
        :param low_memory: 
        :param sep: 
        :param encoding: 
        :param dtype: 
        :return: Pandas DataFrame object
        """
        try:
            return pd.read_csv(path, parse_dates=parse_dates, header=header,
                               low_memory=low_memory, sep=sep, encoding=encoding, dtype=dtype)
        except:
            return pd.DataFrame()

    def remove_json_file(self, file_name):
        """
        Removes raw json file
        """
        file_path = self.raw_json_file_location + "\%s" % file_name
        self.remove_file_or_directory(file_path)

    def remove_file(self, file_path):
        """
        Removes file from FileSystem
        """
        try:
            os.remove(file_path)
        except Exception as e:
            print(e)

    def remove_directory(self, dir_path):
        """
        Removes file from FileSystem
        """
        shutil.rmtree(dir_path)

    def write_csv(self, csv_path, data, separator=','):
        """
        Writes Pandas DataFrame object to FileSystem
        """
        self.check_and_create_path(csv_path)
        data.to_csv(csv_path, index=False, encoding=self.const.ENCODING_UTF8, sep=separator)

    def write_json(self, path, data):
        """
        Writes JSON object to FileSystem
        """
        self.check_and_create_path(path)
        with open(path, "w") as outfile:
            json.dump(data, outfile)

    def write_map(self, map_path, trip_map):
        """
        Writes GoogleMap to FileSystem
        """
        self.check_and_create_path(map_path)
        trip_map.draw(map_path)

    def write_plot(self, plot_path, plot, format="png"):
        """
        Exports Matplotlib based plot to FileSystem
        :param plot_path: plot output path
        :param plot: Matplot lib Plot object
        :param format: output format
        """
        self.check_and_create_path(plot_path)
        plot.savefig(plot_path, format=format)
        plot.close()

    def move_directory(self, source_dir, dest_dir):
        """
        Creates (if required) and move directory to destination folder
        :param source_dir: source directory
        :param dest_dir: destination directory
        """
        self.check_and_create_path(dest_dir)
        try:
            shutil.move(source_dir, dest_dir)
        except Exception as e:
            print(e)

    def create_empty_file(self, file_path):
        """
        Creates empty file in file_path path
        :param file_path: str representing file path
        :return:
        """
        self.check_and_create_path(file_path)
        open(file_path, 'a').close()
        return file_path

    def write_text(self, file_path, text):
        """
        Writes content to file
        :param text:
        :param file_path:
        :return:
        """
        self.check_and_create_path(file_path)
        with open(file_path, "w") as text_file:
            text_file.write(text)

    def read_file_contents_as_string(self, file_path):
        """

        :param file_path:
        :return:
        """
        with open(file_path, 'r') as file_stream:
            return file_stream.read()

    def copy_file(self, source_file, destination_file):
        """

        :param source_file:
        :param destination_file:
        :return:
        """
        self.check_and_create_path(destination_file)
        copyfile(source_file, destination_file)

    def append_to_file(self, file_path, text_value):
        """
        Appends content to the end of file
        :param file_path:
        :param text_value:
        :return:
        """
        if not self.file_exists(file_path):
            self.create_empty_file(file_path)

        with open(file_path, 'a') as file_buffer:
            file_buffer.write(text_value.encode('utf-8'))