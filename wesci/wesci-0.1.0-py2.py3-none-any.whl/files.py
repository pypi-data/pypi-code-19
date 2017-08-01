from timer import Timer
from hash import Hash


class Files(object):

    @staticmethod
    def generate_data_for_log(files_dict):
        data_for_log = {}
        for name, path in files_dict.items():
            data, read_duration = Files.__get_file_data_and_duration_of_read(
                path)
            file_hash, hash_duration = Files.__calc_hash_and_duration(data)
            size = len(data)
            data_for_log[name] = Files.__format_data_for_log(
                path,
                file_hash,
                size,
                read_duration,
                hash_duration)
        return data_for_log

    @staticmethod
    def __calc_hash_and_duration(file_data):
        with Timer() as timer:
            res = Hash.hash(file_data)
        return res, timer.duration_ms()

    @staticmethod
    def __get_file_data_and_duration_of_read(file_path):
        with Timer() as timer:
            with open(file_path) as f:
                file_data = f.read()
        return file_data, timer.duration_ms()

    @staticmethod
    def __format_data_for_log(path, file_hash, size, read_duration, hash_duration):
        return {'path': path,
                'hash': file_hash,
                'size': size,
                'timing': {
                    'file_read_ms': read_duration,
                    'hash_calc_ms': hash_duration},
                }
