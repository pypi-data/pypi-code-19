from bgparsers import readers


def __skip(row, where):
    # TODO Implement where using annotations

    if where is None:
        return False

    for k, v in where.items():
        if str(row.get(k, None)) != v:
            return True
    return False


def run(selection, where=None, groupby=None):

    i = 0
    input_file, input_annotations = selection

    if groupby is None:
        for r in readers.variants(input_file, annotations=input_annotations):

            if __skip(r, where):
                continue

            i += 1
        return i, None
    else:
        groups = {}
        for r in readers.variants(input_file, annotations=input_annotations):

            if __skip(r, where):
                continue

            val = r[groupby]
            val_count = groups.get(val, 0)
            groups[val] = val_count + 1
            i += 1

        return i, groups


