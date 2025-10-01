import datetime
import pytz


def current_time() -> datetime.datetime:
    """
    Returns the current time in the America/Chicago timezone as a datetime object.
    """
    current_time: datetime.datetime = datetime.datetime.now(pytz.timezone("America/Chicago"))
    return current_time
