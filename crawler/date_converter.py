from datetime import datetime, timedelta


def parse_time_ago(
    time_ago: str,
) -> str:
    words = time_ago.split()

    value = int(words[0])
    unit = words[1].lower()

    if unit == "years" or unit == "year":
        delta = timedelta(days=365 * value)
    elif unit == "months" or unit == "month":
        delta = timedelta(days=30 * value)
    elif unit == "weeks" or unit == "week":
        delta = timedelta(weeks=value)
    elif unit == "days" or unit == "day":
        delta = timedelta(days=value)
    elif unit == "hours" or unit == "hour":
        delta = timedelta(hours=value)
    elif unit == "minutes" or unit == "minute":
        delta = timedelta(minutes=value)
    elif unit == "seconds" or unit == "second":
        delta = timedelta(minutes=value)
    else:
        raise ValueError

    current_time = datetime.now()
    result_date = current_time - delta

    result_date = result_date.date()

    return result_date
