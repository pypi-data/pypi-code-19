from pathlib import Path
from random import random


class Folder(object):
    """
    Folder object based around pathlib.
    """
    def __init__(self,folder_path,):
        super(Folder, self).__init__()

        self.accepted_types = None
        self.recursive = False

        self.path = folder_path




    def __str__(self):
        return str(self.path)

    def __iter__(self):
        for x in self.files:
            yield x

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self,folder_path):
        """
        Take a string or Path object as input.
        :param folder_path:
        :return:
        """
        p = Path(folder_path)
        p.resolve()
        if p.exists():

            self._path = p


        else:
            #print("Path does not exist.")
            raise FileNotFoundError
        #
        #
    @property
    def accepted_types(self):
        return self._accepted_types

    @accepted_types.setter
    def accepted_types(self,types):
        if type(types) == list or type(types) == tuple:
            pass
        elif types == None:
            pass
        else:
            raise TypeError("Only accepts list or tupples")

        self._accepted_types = types
    @property
    def recursive(self):
        return self._recursive

    @recursive.setter
    def recursive(self,r):
        if type(r) == bool:
            pass

        else:
            raise TypeError("Only accepts True or False")

        self._recursive = r

    @property
    def files(self):
        if self.accepted_types:
            #print("updating files")
            #print(self.accepted_types)
            if self.recursive:
                files = []
                for e in self.accepted_types:
                    # recursive search for accepted from top folder
                    for f in self.path.rglob("*" + e):
                        if not f.name.startswith(".") and f.is_file():
                            files.append(f)

                return files
            else:
                # only accepted filetypes in top folder
                return [x for x in self.path.iterdir() if x.suffix in self.accepted_types]
        else:
            # all files from current folder
            return [x for x in self.path.iterdir() if x.is_file()]

    @property
    def folders(self):
        if self.recursive:
            folds = []
            for f in self.path.rglob("**"):
                if f.is_dir():
                    folds.append(f)
        else:

            folds = [x for x in self.path.iterdir() if x.is_dir()]

        return folds

    @property
    def randomFile(self):
        return self.files[int(random() * len(self.files))]
