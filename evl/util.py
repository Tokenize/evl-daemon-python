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
