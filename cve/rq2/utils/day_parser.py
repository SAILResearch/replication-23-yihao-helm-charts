from datetime import datetime

def parse_days(created_at, closed_at):

    # Convert the date strings to datetime objects
    created_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    closed_date = datetime.strptime(closed_at, "%Y-%m-%dT%H:%M:%SZ")

    # Calculate the difference between the two dates
    time_difference = closed_date - created_date

    # Extract the number of days from the time difference
    days = time_difference.days

    return days