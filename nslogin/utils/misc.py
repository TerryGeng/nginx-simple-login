def safeget(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct


def get(dct, *keys):
    for key in keys:
        dct = dct[key]
    return dct
