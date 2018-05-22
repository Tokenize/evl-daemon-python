def merge_dicts(default: dict, overrides: dict=None) -> dict:
    """
    Merge given default dictionary of values with given overrides.
    :param default: Default dictionary of values
    :param overrides: Dictionary of value overrides
    :return: Merged dictionary
    """
    if overrides:
        return {**default, **overrides}
    return default


def describe_dict(d: dict) -> list:
    """
    Returns a list of dicts containing the key and value as the 'number' and
    'name' keys.
    :param d: Dictionary to describe
    :return: List of name, number dicts
    """
    return [{'name': name, 'number': number} for name, number in d.items()]