import datetime as dt


def filter_none_values(_list: list) -> list:
    return [i for i in _list if i is not None]


def time_from_string(timestr: str) -> dt.datetime:
    return dt.datetime.strptime(timestr, '%Y-%m-%dT%H:%M:%SZ')
