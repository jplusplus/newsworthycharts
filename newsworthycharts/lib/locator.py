""" Custom locators and related methods
"""
from matplotlib.dates import YearLocator, MonthLocator, DayLocator
from datetime import datetime


def get_year_ticks(start_date, end_date, max_ticks=5):
    """ Get `max_ticks` or less evenly distributed yearly ticks, including
    start and end years. All ticks fall on January 1.
    """

    years = range(start_date.year, end_date.year+1)
    n_years = len(years)
    max_ticks = min(max_ticks, n_years)
    # Avoid N2 < ticks < N, where there will be odd looking gaps
    if n_years > 3:
        if round(n_years/2) < max_ticks < n_years:
            max_ticks = round(n_years/2)

    # -2 for the ends
    # +1 because cutting a cake in n+1 pieces gives n cuts
    if max_ticks > 1:
        cuts = n_years/(max_ticks-2+1)
    else:
        cuts = 0
    selected_years = [years[int(x * cuts)] for x in range(0, max_ticks-1)]

    # add last year
    if max_ticks > 0:
        selected_years.append(years[-1])

    # Ticks should be on the first day of the year
    selected_dates = [datetime(y, 1, 1) for y in selected_years]
    return selected_dates


def get_best_locator(delta, points):
    """ Get the optimal locator given a time delta and number of points.
    This methods will be much more conservative than Matplotlib's AutoLocator,
    trying to keep the x axis as clean as possible, while still including
    enough clues for the reader to easily understand the graph.
    """
    if delta.days > 365*150:
        return YearLocator(100)
    if delta.days > 365*45:
        return YearLocator(20)
    elif delta.days > 365:
        if points > 20:
            return YearLocator(10)
        elif points > 10:
            return YearLocator(5)
        elif points > 5:
            return YearLocator(2)
        else:
            return YearLocator()
    elif delta.days > 30:
        # FIXME dont print every month
        return MonthLocator()
    else:
        return DayLocator()
