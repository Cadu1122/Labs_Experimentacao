def safe_get_value(data: dict, paths: tuple[str], default_value = None):
    value = default_value
    for path in paths:
        if value:
            value = value.get(path)
        else:
            value = data.get(path)
    return value