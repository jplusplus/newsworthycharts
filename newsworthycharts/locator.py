""" Custom locators and related methods
"""
from matplotlib.dates import YearLocator, MonthLocator, DayLocator


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
