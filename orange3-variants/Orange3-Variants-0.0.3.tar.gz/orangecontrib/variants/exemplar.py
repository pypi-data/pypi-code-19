from Orange.data import Instance, Table
from Orange.statistics import distribution


def get_groups(data, group_by):
    if group_by not in data.domain:
        raise ValueError('{} not in domain'.format(group_by))
    var = data.domain[group_by]
    values = var.values if var.is_discrete else sorted(
        set(ins[group_by].value for ins in data))
    groups = [[i for i in data if i[var] == v] for v in values]
    return [Table(data.domain, g) for g in groups if g]


def centroid(data, group_by=None):
    if group_by is not None:
        groups = get_groups(data, group_by)
        reps = [centroid(g) for g in groups]
        return Table(data.domain, reps)
    dist = distribution.get_distributions(data)
    # TODO: handle metas as well
    c = Instance(data.domain, [(d.mean() if d.variable.is_continuous else d.modus()) for d in dist])
    return c


def medoid(data, group_by=None):
    if group_by is not None:
        groups = get_groups(data, group_by)
        reps = [medoid(g) for g in groups]
        return Table(data.domain, reps)
    return data[0]


if __name__ == '__main__':
    data = Table('iris')
    print(centroid(data))
    print(centroid(data, 'iris'))
    print(medoid(data))
