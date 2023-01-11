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

    def _get_bar_colors(self, i, *args):
        if not self.data:
            # Don't waste time
            return None
        interval = self.interval or self._guess_interval()
        # Use either highlight or last point of the series that extends furthest to the right
        seasonal_point = self.highlight or self.data.outer_max_x
        if interval == "monthly":
            date_suffix = seasonal_point[-5:]
        else:
            raise NotImplementedError("Seasonal chart currently only supports monthly data")

        color_s = self._nwc_style["dark_gray_color"]
        color_n = self._nwc_style["light_gray_color"]
        colors = [color_s if x[0].endswith(date_suffix) else color_n
                  for x in self.data[i]]

        # Highlight latest by default
        if self.highlight:
            for i, d in enumerate(self.data[i]):
                if d[0] == self.highlight:
                    colors[i] = self._nwc_style["strong_color"]
        else:
            colors[-1] = self._nwc_style["strong_color"]

        # If we want to suppport multiple series
        # if i > 0:
        #    color_s = self._nwc_style["dark_gray_color"]
        #    color_n = self._nwc_style["light_gray_color"]
        #    colors = [color_s if x[1].endswith(date_suffix) else color_n
        #              for x in self.data[0]]

        return colors
