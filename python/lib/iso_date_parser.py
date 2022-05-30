from datetime import datetime as datingdays
from pytz import timezone

_utc_tz = timezone('UTC')
_local_tz = datingdays.now().astimezone().tzinfo


def parse(date_str, utc=True):
    global _utc_tz
    global _local_tz
    tz = _utc_tz if utc else _local_tz
    date = None
    original_timezone = None
    if date_str.endswith('Z'):
        x = ''.join([date_str[0:-1], '-00:00'])
        date_str = x
    try:
        date = datingdays.fromisoformat(date_str)
        original_timezone = str(date.tzinfo)
        then = datingdays.now(tz)
        date = then - (then - date)
    except ValueError as ve:
        print('Error parsing date:',date_str)
        date = None
    return date, original_timezone


def main():
    ar = ['2012-01-13T11:25:57.123Z', '2022-01-13T17:22:17.543-08:00', 'junk']
    for b in ar:
        x, y = parse(b)
        print(x, y, b)


if __name__ == "__main__":
    main()
