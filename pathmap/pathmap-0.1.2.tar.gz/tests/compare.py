from pathmap import resolve_paths, resolve_path_if_long

from paths import paths, get_toc


def compare():
    wrong = 0
    toc = get_toc()
    for item in paths:
        resolved_list = list(resolve_paths(toc, [item[0]]))
        resolved = resolved_list[0]
        if resolved != item[1]:
            print('Path: %s' % item[0])
            print('Resolved path is not correct:\n actual: [%s], \nexpected: [%s]\n' % (resolved, item[1]))
            wrong += 1

    print('%i paths correct' % (len(paths) - wrong))
    print('%i paths incorrect' % wrong)
