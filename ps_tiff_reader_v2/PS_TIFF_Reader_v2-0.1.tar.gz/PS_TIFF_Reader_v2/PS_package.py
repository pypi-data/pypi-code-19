
from struct import pack as _pack
from struct import unpack as _unpack

def pack(kv, struct):
    data = ''

    for typ, key, default, desc in struct:
        val = kv.get(key, default)

        if 'i' in typ and len(desc) > 0:
            if val in desc:
                val = desc.index(val)
            else:
                raise ValueError('%s can be %s not %s' % (key, desc, val))

        if 's' in typ:
            l = int(typ[0:-1])
            val = val.encode('UTF-16')[2:l]
            val = val + '\0' * (l - len(val))

        else:
            val = _pack('<'+typ, val)

        data = data + val
    return data

def unpack(data, struct):
    ret = {}
    fmt = '<'

    for typ, key, default, desc in struct:
        fmt = fmt + typ
    data = _unpack(fmt, data)

    i = 0
    for typ, key, default, desc in struct:
        if 'i' in typ:
            v = int(data[i])
            l = len(desc)
            if l > 0 and v < l:
                ret[key] = desc[v]
            else:
                ret[key] = v

        elif 's' in typ:
            if key is not 'Reserved':
                #ret[key] = unicode(data[i], 'UTF-16').replace('\0', '')
                ret[key] = data[i]

        else:
            ret[key] = float(data[i])

        i = i + 1

    return ret
