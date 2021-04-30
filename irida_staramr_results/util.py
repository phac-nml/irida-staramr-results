from datetime import datetime, timezone
from dateutil import tz


def local_to_timestamp(target_date):
    """
    Converts date in local time to unix timestamp in milliseconds. Assumes "YYYY-mm-dd" is the input date format.
    :param target_date: string type formatted as YYYY-mm-dd
    :return:
    """

    dt_local = datetime.strptime(target_date, "%Y-%m-%d")  # local
    dt_utc = dt_local.replace(tzinfo=timezone.utc)  # local -> utc
    timestamp = dt_utc.timestamp() * 1000  # utc -> unix timestamp (millisecond)

    return timestamp


def timestamp_to_local(timestamp):
    """
    Converts unix timestamp in milliseconds to local time.
    :param timestamp:
    :return: string type formatted as YYYY-mm-dd
    """
    timestamp = timestamp/1000
    local_tz = tz.tzlocal()

    dt_utc = datetime.utcfromtimestamp(timestamp)
    dt_local = dt_utc.replace(tzinfo=local_tz)
    date_str = dt_local.strftime("%Y-%m-%d")
    return date_str
