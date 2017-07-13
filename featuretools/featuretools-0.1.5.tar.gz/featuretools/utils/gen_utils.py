def topsort(nodes, depfunc):
    queue = nodes[:]
    ordered = []
    while queue:
        next_n = queue.pop(0)
        for dep in depfunc(next_n):
            if dep in ordered:
                ordered.remove(dep)
            queue.append(dep)
        if next_n in ordered:
            ordered.remove(next_n)
        ordered.append(next_n)
    return ordered[::-1]
