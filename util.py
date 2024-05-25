import pandas as pd

def get_weekdays(date_range):
    """Generate a list of weekdays between start_date and end_date"""
    start_date, end_date = date_range
    all_dates = pd.date_range(start=start_date, end=end_date, freq='B')  # 'B' frequency stands for business days
    return [date.strftime('%Y-%m-%d') for date in all_dates]