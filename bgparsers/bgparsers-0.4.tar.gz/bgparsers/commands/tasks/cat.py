from bgparsers import readers


def __skip(row, where):
    if where is None:
        return False

    for k, v in where.items():
        if str(row.get(k, None)) != v:
            return True
    return False


def run(selection, where=None):

    try:
        headers = ["SAMPLE", "DONOR", "CHROMOSOME", "POSITION", "REF", "ALT", "STRAND", "ALT_TYPE"]
        print("\t".join(headers))
        for input_file, input_annotations in selection:
            for r in readers.variants(input_file, annotations=input_annotations):

                # TODO Implement where using annotations
                if __skip(r, where):
                    continue

                print("\t".join([str(r.get(h, "")) for h in headers]))
    except BrokenPipeError:
        pass

