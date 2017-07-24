class MultiDict(dict):
    @classmethod
    def from_list(cls, l):
        d = cls()
        for k, v in l:
            if k in d:
                d[k].add(v)
            else:
                d[k] = {v}
        return d
