class Config(object):
    def load(self, conf_file_path):
        with open(conf_file_path) as f:
            content = f.readlines()
        self.__api_key = content[0].strip()

    def api_key(self):
        return self.__api_key
