class Error(ValueError):
    def __init__(self, item, container_name):
        self.item = item
        self.container_name = container_name

    def __str__(self):
        return '{item} does not all exist in {container_name}'.format(item=self.item,
                                                                      container_name=self.container_name)

class Choice:
    def __init__(self, *pairs):
        self._choices = pairs

    def __getitem__(self, index):
        if index is Ellipsis:
            return [n for i, n in self._choices]
        elif isinstance(index, tuple):
            rv = [n for i, n in self._choices if i in index]
            if len(rv) != len(index):
                raise Error(index, self.__class__.__name__)
            return rv
        else:
            for i, n in self._choices:
                if i == index:
                    return n
            raise Error(index, self.__class__.__name__)

    def __call__(self, *names):
        if len(names) == 0:
            return [i for i, n in self._choices]
        elif len(names) == 1:
            name = names[0]
            for i, n in self._choices:
                if n == name:
                    return i
            raise Error(name, self.__class__.__name__)
        else:
            rv = [i for i, n in self._choices if n in names]
            if len(rv) != len(names):
                raise Error(names, self.__class__.__name__)
            return rv

    def exclude(self, *names):
        rv = []
        is_in_choice = [False for x in names]
        idx = 0
        for i, n in self._choices:
            if n not in names:
                rv.append(i)
            else:
                is_in_choice[idx] = True
                idx += 1
        if not all(is_in_choice):
            raise Error(names, self.__class__.__name__)
        return rv

    def pairs(self, *names):
        if names:
            rv = [(i, n) for i, n in self._choices if n in names]
            if len(rv) != len(names):
                raise Error(names, self.__class__.__name__)
        else:
            rv = [(i, n) for i, n in self._choices]
        return rv
