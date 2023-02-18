"""Utilities for dealing with times."""
from datetime import datetime


def is_current_time_between(time_from, time_till):
    """Returns True if current time is in the given time span."""
    if time_from == time_till:
        return False
    current_time = datetime.now().time()
    if time_from < time_till:
        return time_from <= current_time <= time_till
    return current_time >= time_from or current_time <= time_till


def get_diff_in_secs(time_a, time_b):
    """Convert time to seconds since midnight and return the absolute difference."""
    a_secs = (time_a.hour * 60 + time_a.minute) * 60 + time_a.second
    b_secs = (time_b.hour * 60 + time_b.minute) * 60 + time_b.second
    if a_secs < b_secs:
        return b_secs - a_secs
    return a_secs - b_secs
