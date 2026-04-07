from datetime import datetime, timedelta
# datetime:
# - Used to work with dates AND times

# timedelta:
# - Represents a duration of time (e.g., days, hours, minutes)
# - Used for date/time arithmetic

def will_make_shuttle(current_time, walking_minutes, shuttle_arrival_time):
    """Determines if user will make the shuttle"""

    arrival_at_shuttle_stop = current_time + timedelta(minutes = walking_minutes)
    return arrival_at_shuttle_stop <= shuttle_arrival_time


def recommended_leave_time(walking_minutes, shuttle_arrival_time):
    """Calculates when the user should leave to catch the shuttle"""

    return shuttle_arrival_time - timedelta(minutes = walking_minutes)


def find_next_shuttle(current_time, shuttle_times):
    """Finds the next available shuttle after current time"""

    for shuttle_time in shuttle_times:
        if shuttle_time > current_time:
            return shuttle_time
    return None