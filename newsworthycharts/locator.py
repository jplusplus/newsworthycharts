""" Custom locators and related methods
"""
from matplotlib.dates import YearLocator, MonthLocator, DayLocator
from datetime import datetime


def get_year_ticks(dates, max_ticks=5):
    """ Get `max_ticks` evenly distributed yearly ticks from a list of dates,
    including start and end dates.
    """

    # Get unique years in the data
    years = sorted(list(set([y.year for y in dates])))
    max_ticks = min(max_ticks, len(years))
    # -2 for the ends
    # +1 because cutting a cake in n+1 pieces gives n cuts
    if max_ticks > 1:
        cuts = len(years)/(max_ticks-2+1)
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
