
class DKFileUtils:
    def __init__(self):
        pass

    @staticmethod
    def is_file_contents_binary(file_contents):
        '''
        Check for binary files
        :param file_contents: The contents of the file, for instance, the outcome of f.read()
        :return:
        '''
        try:
            file_contents.encode('utf8')
            return False
        except:
            return True