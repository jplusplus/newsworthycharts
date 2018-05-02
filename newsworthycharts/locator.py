""" Custom locators and related methods
"""
from matplotlib.dates import YearLocator, MonthLocator, DayLocator
from matplotlib.ticker import MaxNLocator


def get_best_locator(delta, points):
    """ Get the optimal locator given a time delta and number of points.
    This methods will be much more conservative than Matplotlib's AutoLocator,
    trying to keep the x axis as clean as possible, while still including
    enough clues for the reader to easily understand the graph.
    """
    if delta.months > 12:
        if points > 4:
            return MaxNLocator(5)
        else:
            return YearLocator
    elif delta.months > 1:
        return MonthLocator
    else:
        return DayLocator
