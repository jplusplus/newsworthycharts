"""
The “seasonal chart”, aka “Olsson chart” will highlight each corresponding
time point (day, week, month, ...) during earlier periods (typically a year)
"""
from .serialchart import SerialChart


class SeasonalChart(SerialChart):
    """Plot a timeseries, as a line or bar plot, highlighting
    a specific period (e.g. month) each time it appears.

    Data should be a list of iterables of (value, date string) tuples, eg:
    `[ [("2010-01-01", 2), ("2010-02-01", 2.3)] ]`
    """

    def __init__(self, *args, **kwargs):
        super(SeasonalChart, self).__init__(*args, **kwargs)

        # Optional: where to place series label
        self.label_placement = "legend"  # "legend"|"line|inline"

    @property
    def colors(self):
        colors_prim = []
        colors = [colors_prim]
        if len(self.data) > 1:
            colors_second = []
            colors.append(colors_second)
        return colors
