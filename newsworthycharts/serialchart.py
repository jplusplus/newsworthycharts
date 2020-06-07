from .chart import Chart
from .lib.locator import get_best_locator, get_year_ticks
from .lib.utils import to_float, to_date
from .lib.formatter import Formatter

import numpy as np
from math import inf
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import (DateFormatter, YearLocator, MonthLocator,
                              DayLocator, WeekdayLocator)
from dateutil.relativedelta import relativedelta


class SerialChart(Chart):
    """Plot a timeseries, as a line or bar plot.

    Data should be a list of iterables of (value, date string) tuples, eg:
    `[ [("2010-01-01", 2), ("2010-02-01", 2.3)] ]`
    """

    def __init__(self, *args, **kwargs):
        super(SerialChart, self).__init__(*args, **kwargs)
        self.type = "bars"
        self.bar_width = 0.9
        # Percent of period. 0.85 means a bar in a chart with yearly data will
        # be around 310 or 311 days wide.
        self.max_ticks = 5
        self._ymin = None
        self._ymax = None

    @property
    def ymin(self):
        # WIP
        return self._ymin

    @ymin.setter
    def ymin(self, val):
        self._ymin = val

    @property
    def ymax(self):
        return self._ymax

    @ymax.setter
    def ymax(self, val):
        self._ymax = val

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, val):
        if val in ["bars", "line"]:
            self._type = val
        else:
            raise ValueError("Supported types are bars and line")

    def _days_in(self, interval, d=None):
        """Return number of days in a given period.

        If only interval is given, use a typical number of days.
        >>>> _days_in(monthly)
        30
        >>>> _days_in(monthly, datetime(2004, 02, 05))
        29
        """
        if d is None:
            return {
                'yearly': 365,
                'quarterly': 91,
                'monthly': 30,
                'weekly': 7,
                'daily': 1,
            }[interval]
        else:
            # https://stackoverflow.com/questions/4938429/how-do-we-determine-the-number-of-days-for-a-given-month-in-python

            if interval == "yearly":
                return (
                    (d + relativedelta(years=1)).replace(day=1, month=1) - d.replace(day=1, month=1)
                ).days
            elif interval == "quarterly":
                return (
                    (d + relativedelta(months=3)).replace(day=1) - d.replace(day=1)
                ).days
            elif interval == "monthly":
                return (
                    (d + relativedelta(months=1)).replace(day=1) - d.replace(day=1)
                ).days
            elif interval == "weekly":
                # Assuming ISO 8601 here
                return 7
            elif interval == "daily":
                return 1

    def _guess_interval(self):
        """Return a probable interval, e.g. "montly", given current data."""
        interval = "yearly"
        for serie in self.data:
            dates = [to_date(x[0]) for x in serie]
            years = [x.year for x in dates]
            months = [x.month for x in dates]
            yearmonths = [x[0][:7] for x in serie]
            weeks = [str(x.year) + str(x.isocalendar()[1]) for x in dates]
            if len(years) > len(set(years)):
                # there are years with more than one point
                if all(m in [1, 4, 7, 10] for m in months):
                    interval = "quarterly"
                else:
                    interval = "monthly"
                    if len(yearmonths) > len(set(yearmonths)):
                        interval = "weekly"
                    if len(weeks) > len(set(weeks)):
                        interval = "daily"
        return interval

    def _get_annotation_direction(self, index, values):
        """ Given an index and series of values, provide the estimated best
        direction for an annotation. This will be an educated guess, and the
        annotation is not guaranteed to be free from overlapping,
        """
        num_vals = len(values)
        if num_vals < 2:
            return "up"
        if index == 0:
            if values[0] < values[1]:
                return "down"
            else:
                return "up"
        if index == num_vals - 1:
            # get previous non-None value
            latest_not_null = [x for x in values[:-1] if x is not None][-1]
            if latest_not_null <= values[-1]:
                return "up"
            else:
                return "down"
        val = values[index]
        if val == max(values[index - 1:index + 2]):
            return "up"
        if val == min(values[index - 1:index + 2]):
            return "down"
        return "up"

    def _add_data(self):

        series = self.data
        is_stacked = (len(series) > 1) and (self.type == "bars")

        # parse values
        serie_values = []
        for serie in series:
            _values = [to_float(x[1]) for x in serie]
            if self.type == "bars":
                # Replace None values with 0's to be able to plot bars
                _values = [0 if v is None else v for v in _values]
            serie_values.append(_values)


        # Select a date to highlight
        if self.highlight is not None:
            try:
                highlight_date = to_date(self.highlight)
            except ValueError:
                # in case we are highlighting something else (like a whole serie)
                highlight_date = None

        # Make an educated guess about the interval of the data
        if self.interval is None:
            self.interval = self._guess_interval()

        # Formatters for axis and annotations
        y_formatter = self._get_value_axis_formatter()
        a_formatter = self._get_annotation_formatter()

        # Number of days on x axis (Matplotlib will use days as unit here)
        xmin, xmax = to_date(self.data.x_points[0]), to_date(self.data.x_points[-1])
        delta = xmax - xmin

        # Store y values while we are looping the data, to adjust axis,
        # and highlight diff
        highlight_diff = {
            'y0': inf,
            'y1': -inf
        }
        highlight_values = []
        for i, serie in enumerate(series):
            # Use strong color for first series
            if i == 0:
                color = self._style["strong_color"]
            else:
                color = self._style["neutral_color"]

            values = serie_values[i]
            dates = [to_date(x[0]) for x in serie]

            highlight_value = None
            if self.highlight:
                try:
                    highlight_value = values[dates.index(highlight_date)]
                    highlight_values.append(highlight_value)
                except ValueError:
                    # If this date is not in series, silently ignore
                    pass

            if self.highlight and (highlight_value is not None):
                highlight_diff['y0'] = min(highlight_diff['y0'],
                                           highlight_value)
                highlight_diff['y1'] = max(highlight_diff['y1'],
                                           highlight_value)
            if self.type == "line":
                # Put first series on top
                zo = 2 + (i == 0)
                line, = self.ax.plot(dates, values,
                                     color=color,
                                     zorder=zo)
                # Add single, orphaned data points as markers
                # None, 1, None, 1, 1, 1 =>  . ---
                num_values = len(values)
                if num_values == 1:
                    self.ax.plot(dates[0], values[0],
                                 c=color,
                                 marker='.',
                                 zorder=2)
                elif num_values > 1:
                    for j, v in enumerate(values):
                        plot_me = False
                        if v is not None:
                            if j == 0 and (values[j + 1] is None):
                                plot_me = True
                            elif j == num_values - 1 and (values[j - 1] is None):
                                plot_me = True
                            elif (values[j - 1] is None) and (values[j + 1] is None):
                                plot_me = True
                        if plot_me:
                            self.ax.plot(dates[j], v,
                                         c=color,
                                         marker='.',
                                         zorder=2)

                if len(self.labels) > i:
                    line.set_label(self.labels[i])

                # add highlight marker
                if highlight_value:
                    self.ax.plot(highlight_date, highlight_value,
                                 c=color,
                                 marker='o',
                                 zorder=2)

            elif self.type == "bars":
                # aggregate values for stacked bar chart
                # TODO: Consider moving this logic to `lib.datalist.DataList`
                cum_values = np.cumsum(serie_values, axis=0).tolist()

                if is_stacked:
                    if self.highlight:
                        if self.highlight == self.labels[i]:
                            color = self._style["strong_color"]
                        else:
                            color = self._style["neutral_color"]
                    else:
                        color = self._style["qualitative_colors"][i]
                    colors = [color] * len(values)

                else: # only one series
                    # Pick color based on value of each bar
                    if self.color_fn:
                        colors = [self._color_by(v) for v in values]

                    elif self.highlight:
                        colors = []
                        for timepoint in dates:
                            if highlight_value and timepoint == highlight_date:
                                colors.append(self._style["strong_color"])
                            else:
                                colors.append(self._style["neutral_color"])
                    else:
                        # use strong color if there is no highlight
                        colors = [self._style["strong_color"]] * len(dates)

                # Set bar width, based on interval
                bar_lengths = [self._days_in(self.interval, d) for d in dates]
                bar_widths = [l * self.bar_width for l in bar_lengths]

                # If there are too many ticks per pixel,
                # don't put whitespace betw bars. Make widths = 1
                bbox = self.ax.get_window_extent()
                if (sum(bar_widths) * 2 / len(dates)) > bbox.width:
                    bar_widths = [l * 1 for l in bar_lengths]

                bar_kwargs = dict(
                    color=colors,
                    width=bar_widths,
                    zorder=2
                )
                if i > 0:
                    # To make stacked bars we need to set bottom value
                    bar_kwargs["bottom"] = cum_values[i-1]
                bars = self.ax.bar(dates, values, **bar_kwargs)

                if len(self.labels) > i:
                    bars.set_label(self.labels[i])

        # Annotate highlighted points/bars
        for hv in highlight_values:
            value_label = a_formatter(hv)
            xy = (highlight_date, hv)
            if self.type == "bars":
                if hv >= 0:
                    dir = "up"
                else:
                    dir = "down"
            if self.type == "line":
                if len(highlight_values) > 1:
                    # When highlighting two values on the same point,
                    # put them in opposite direction
                    if hv == max(highlight_values):
                        dir = "up"
                    elif hv == min(highlight_values):
                        dir = "down"
                    else:
                        dir = "left"  # To the right we have diff annotation
                else:
                    # Otherwise, use what works best with the line shape
                    i = dates.index(highlight_date)
                    dir = self._get_annotation_direction(i, values)
            self._annotate_point(value_label, xy, direction=dir)

        # Accentuate y=0
        if self.data.min_val < 0:
            self.ax.axhline(linewidth=1)

        # Highlight diff
        y0, y1 = highlight_diff['y0'], highlight_diff['y1']
        # Only if more than one series has a value at this point, and they
        # actually look different
        if self.highlight and\
           (len(highlight_values) > 1) and\
           (a_formatter(y0) != a_formatter(y1)) and\
           self.type == "line":

            self.ax.vlines(highlight_date, y0, y1,
                           colors=self._style["neutral_color"],
                           linestyles='dashed')
            diff = a_formatter(abs(y0 - y1))
            xy = (highlight_date, (y0 + y1) / 2)
            self._annotate_point(diff, xy, direction="right")

        # Shade area between lines if there are exactly 2 series
        # For more series, the chart will get messy with shading
        if len(series) == 2:
            # Fill any gaps in series
            filled_values = self.data.filled_values
            min_x = self.data.inner_min_x
            max_x = self.data.inner_max_x
            self.ax.fill_between([to_date(x) for x in self.data.x_points],
                                 filled_values[0],  # already a float1w
                                 filled_values[1],
                                 where=[(x >= min_x and x <= max_x)
                                        for x in self.data.x_points],
                                 facecolor=self._style["fill_between_color"],
                                 alpha=self._style["fill_between_alpha"])

        # Y axis formatting
        padding_bottom = abs(self.data.min_val * 0.15)
        if self.ymin is not None:
            ymin = min(self.ymin, self.data.min_val - padding_bottom)
        else:
            ymin = self.data.min_val - padding_bottom

        if self.ymax is not None:
            y_max = max(self.ymax, self.data.max_val)

        else:
            if is_stacked:
                y_max = self.data.stacked_max_val
            else:
                y_max = self.data.max_val

        self.ax.set_ylim(ymin=ymin,
                         ymax=y_max * 1.15)

        self.ax.yaxis.set_major_formatter(y_formatter)
        self.ax.yaxis.grid(True)

        # X ticks and formatter
        if delta.days > 365:
            ticks = get_year_ticks(xmin, xmax, max_ticks=self.max_ticks)
            self.ax.set_xticks(ticks)
            self.ax.xaxis.set_major_formatter(DateFormatter('%Y'))
        else:
            loc = get_best_locator(delta, len(dates), self.interval)
            self.ax.xaxis.set_major_locator(loc)

            if isinstance(loc, WeekdayLocator):
                # We consider dates to be more informative than week numbers
                fmt = DateFormatter('%-d %b')
            elif isinstance(loc, MonthLocator):
                fmt = DateFormatter('%b')
            elif isinstance(loc, DayLocator):
                fmt = DateFormatter('%-d %b')
            else:
                NotImplementedError("Unable to determine tick formatter")

            self.ax.xaxis.set_major_formatter(fmt)

        # Add labels in legend if there are multiple series, otherwise
        # title is assumed to self-explanatory
        if len(self.labels) > 1:
            self.ax.legend(loc='best')

        # Trend/change line
        # Will use first serie
        if self.trendline:
            # Check if we have a list of single (x-) values, or data points
            if all(len(x) == 2 for x in self.trendline):
                # data points
                dates = [to_date(x[0]) for x in self.trendline]
                values = [to_float(x[1]) for x in self.trendline]
                marker = "_"
            else:
                # timepoints, get values from first series
                dates = [to_date(x) for x in self.trendline]
                alldates = [to_date(x[0]) for x in self.data[0]]
                values = [self.data[0][alldates.index(d)][1] for d in dates]
                marker = 'o'

            self.ax.plot(dates, values,
                         color=self._style["strong_color"], zorder=4,
                         marker=marker, linestyle='dashed')

            # Annotate points in trendline
            if self.annotate_trend:
                for i, date in enumerate(dates):
                    xy = (date, values[i])
                    dir = self._get_annotation_direction(i, values)
                    self._annotate_point(a_formatter(values[i]), xy,
                                         color=self._style["strong_color"],
                                         direction=dir)

            # x = [a.xy[0] for a in self._annotations]
            # y = [a.xy[1] for a in self._annotations]
            # adjust_text(self._annotations,
            #             x=x, y=y)
