""" Custom locators and related methods
"""
from matplotlib.dates import YearLocator, MonthLocator, DayLocator


def get_best_locator(delta, points):
    """ Get the optimal locator given a time delta and number of points.
    This methods will be much more conservative than Matplotlib's AutoLocator,
    trying to keep the x axis as clean as possible, while still including
    enough clues for the reader to easily understand the graph.
    """
    if delta.days > 365:
        if points > 20:
            return YearLocator(10)
        elif points > 10:
            return YearLocator(5)
        elif points > 5:
            return YearLocator(2)
        else:
            return YearLocator()
    elif delta.days > 30:
        if points > 8:
            return MonthLocator(4)
        elif points > 5:
            return MonthLocator(2)
        else:
            return MonthLocator()
    else:
        return DayLocator()
