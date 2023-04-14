"""
As stripechart will print a striped bar (or multiple), typically
illustrating a development over time or space
"""
from .chart import Chart
from datetime import datetime
from .lib.utils import to_date


class StripeChart(Chart):
    """Plot a data seriers as a stiped bar.

    Data should be a list of iterables of (date|index, value) tuples, eg:
    `[ [("2010-01-01", 0), ("2010-02-01", 1)] ]`
    ...or:
    `[ [(1, 0), (4, 1)] ]`
    """

    uses_categorical_data = False

    def __init__(self, *args, **kwargs):
        super(StripeChart, self).__init__(*args, **kwargs)
        self.colors = None

    def _add_data(self):
        dates = [to_date(x[0]) for x in self.data[0]]
        for i, serie in enumerate(self.data):
            if self.labels and len(self.labels) > i:
                label = self.labels[i]
            else:
                label = i

            for point in serie:
                date = datetime.strptime(point[0], "%Y-%m-%d")
                value = point[1]
                if self.colors:
                    color = self.colors[value]
                elif value:
                    color = self._nwc_style["strong_color"]
                else:
                    color = self._nwc_style["neutral_color"]
                self.ax.barh(
                    label,
                    width=1,
                    left=date,
                    color=color
                )

        if not self.labels or len(self.labels) is None:
            self.ax.set_yticks([])

        self._set_date_ticks(dates)
