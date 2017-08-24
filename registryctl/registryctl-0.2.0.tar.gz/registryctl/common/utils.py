def columnize_list(columns, list):
    items = []
    for item in list:
        d = []
        for c in columns:
            d.append(item[c])
        items.append(d)

    return (columns, items)
