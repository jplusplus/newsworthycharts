""" Create charts and store them as images.
For use with Newsworthy's robot writer and other similar projects.
"""
from io import BytesIO
from math import inf
from matplotlib.font_manager import FontProperties
from .utils import loadstyle, to_float, to_date
from .mimetypes import MIME_TYPES
from .storage import LocalStorage
from .formatter import Formatter
from .locator import get_best_locator, get_year_ticks
from .datalist import DataList
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import DateFormatter
from langcodes import standardize_tag

image_formats = MIME_TYPES.keys()


class Chart(object):
    """ Convenience wrapper around a Matplotlib figure
    """
    # Properties managed through getters/setters
    _title = None
    _units = "count"

    # Simple properties
    xlabel = None
    ylabel = None
    caption = None
    highlight = None
    # We will try to guess interval based on the data,
    # but explicitly providing a value is safer. Used for finetuning.
    interval = None  # ["yearly", "quarterly", "monthly", "weekly", "daily"]
    annotations = []
    data = DataList()  # A list of datasets
    labels = []  # Optionally one label for each dataset
    trendline = []  # List of x positions, or data points

    _annotations = []


    def __init__(self, width: int, height: int, storage=LocalStorage(),
                 style: str='newsworthy', language: str='en-GB'):
        """
        :param width: width in pixels
        :param height: height in pixels
        :param storage: storage object that will handle file saving. Default
                        LocalStorage() class will save a file the working dir.
        :param style: a predefined style or the path to a custom style file
        :param language: a BCP 47 language tag (eg `en`, `sv-FI`)
        """

        self.storage = storage
        self.w, self.h = width, height
        self.style = loadstyle(style)
        # Standardize and check if language tag is a valid BCP 47 tag
        self.language = standardize_tag(language)

        # Dynamic typography
        self.small_font = FontProperties()
        self.small_font.set_size("small")

        self.title_font = FontProperties()
        self.title_font.set_family(self.style["title_font"])
        self.title_font.set_size(self.style["figure.titlesize"])

        self.fig = Figure()
        FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        # self.fig, self.ax = plt.subplots()

        # Calculate size in inches
        dpi = self.fig.get_dpi()
        real_width = float(width)/dpi
        real_height = float(height)/dpi
        self.fig.set_size_inches(real_width, real_height)

    def _rel_height(self, obj):
        """ Get the relative height of a chart object to the whole canvas.
        """
        # We must draw the figure to know all sizes
        self.fig.draw(renderer=self.fig.canvas.renderer)
        bbox = obj.get_window_extent()
        return bbox.height / float(self.h)

    def _annotate_point(self, text, xy,
                        direction,
                        **kwargs):
        """Adds a label to a given point.

        :param text: text content of label
        :param xy: coordinates to annotate
        :param direction: placement of annotation.
            ("up", "down", "left", "right")
        :param kwags: any params accepted by plt.annotate
        """
        opts = {
            "fontproperties": self.small_font,
            "textcoords": "offset pixels",
        }
        if "color" not in opts:
            opts["color"] = self.style["neutral_color"]

        offset = 16  # px between point and text FIXME remove hardcoded value
        if direction == "up":
            opts["verticalalignment"] = "bottom"
            opts["horizontalalignment"] = "center"
            opts["xytext"] = (0, offset)
        elif direction == "down":
            opts["verticalalignment"] = "top"
            opts["horizontalalignment"] = "center"
            opts["xytext"] = (0, -offset)
        elif direction == "left":
            opts["verticalalignment"] = "center"
            opts["horizontalalignment"] = "right"
            opts["xytext"] = (-offset, 0)
        elif direction == "right":
            opts["verticalalignment"] = "center"
            opts["horizontalalignment"] = "left"
            opts["xytext"] = (offset, 0)
        else:
            msg = "'{}' is an unknown direction for an annotation".format(direction)
            raise Exception(msg)

        # Override default opts if passed to the function
        opts.update(kwargs)

        ann = self.ax.annotate(text, xy=xy, **opts)
        # ann = self.ax.text(text, xy[0], xy[1])
        self._annotations.append(ann)

    def _add_caption(self, caption):
        """ Adds a caption. Supports multiline input.
        """
        text = self.fig.text(0.01, 0.01, caption,
                             color=self.style["neutral_color"], wrap=True,
                             fontproperties=self.small_font)

        # Increase the bottom padding by the height of the text bbox
        margin = self.style["figure.subplot.bottom"]
        margin += self._rel_height(text)
        self.fig.subplots_adjust(bottom=margin)

    def _add_title(self, title_text):
        """ Adds a title """
        text = self.fig.suptitle(title_text, wrap=True,
                                 multialignment="left",
                                 fontproperties=self.title_font)

        padding = self.style["figure.subplot.top"]
        self.fig.subplots_adjust(top=padding)

    def _add_xlabel(self, label):
        """Adds a label to the x axis."""
        self.ax.set_xlabel(label, fontproperties=self.small_font)

    def _add_ylabel(self, label):
        """Adds a label to the y axis."""
        self.ax.set_ylabel(label, fontproperties=self.small_font)

    def _add_data(self):
        """ Plot data to the chart.
        Typically defined by a more specific subclass
        """
        raise NotImplementedError("This method should be overridden")

    def render(self, key, img_format):
        """
         Apply all changes, render file, and send to storage.
        """
        # Apply all changes, in the correct order for consistent rendering
        if len(self.data):
            self._add_data()
        for a in self.annotations:
            self._annotate_point(a["text"], a["xy"], a["direction"])
        if self.ylabel is not None:
            self._add_ylabel(self.ylabel)
        if self.xlabel is not None:
            self._add_xlabel(self.xlabel)
        # tight_layout after _add_caption would ruin extra padding added there
        self.fig.tight_layout()
        if self.title is not None:
            self._add_title(self.title)
        if self.caption is not None:
            self._add_caption(self.caption)

        # Save plot in memory, to write it directly to storage
        buf = BytesIO()
        self.fig.savefig(buf, format=img_format)
        buf.seek(0)
        self.storage.save(key, buf, img_format)

    def render_all(self, key):
        """
        Render all available formats
        """
        for file_format in image_formats:
            self.render(key, file_format)

    @property
    def title(self):
        """ A user could have manipulated the fig property directly,
        so check for a title there as well.
        """
        if self._title is not None:
            return self._title
        elif self.fig._suptitle:
            return self.fig._suptitle.get_text()
        else:
            return None

    @title.setter
    def title(self, t):
        self._title = t

    @property
    def units(self):
        return self._units

    @units.setter
    def units(self, val):
        """ Units, used for number formatting. Note that 'degrees' is designed
        for temperature degrees.
        In some languages there are typographical differences between
        angles and short temperature notation (e.g. 45° vs 45 °).
        """
        allowed_units = ["count", "percent", "degrees"]
        if val in allowed_units:
            self._units = val
        else:
            raise ValueError("Supported units are: {}".format(allowed_units))

    def __str__(self):
        # Return main title or id
        if self.title is not None:
            return self.title
        else:
            return str(id(self))

    def __repr__(self):
        # Use type(self).__name__ to get the right class name for sub classes
        return "<{cls}: {name} ({h} x {w})>".format(cls=type(self).__name__,
                                                    name=str(self),
                                                    w=self.w, h=self.h)


class SerialChart(Chart):
    """ Plot a timeseries, as a line or bar plot. Data should be a list of
    iterables of (value, date string) tuples, eg:
    `[ [("2010-01-01", 2), ("2010-02-01", 2.3)] ]`
    """

    _type = "bars"
    max_ticks = 5
    ymin = 0  # Set this to None to automatically adjust y axis to data

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, val):
        if val in ["bars", "line"]:
            self._type = val
        else:
            raise ValueError("Supported types are bars and line")

    def _days_in(self, interval):
        """ Estimated whole number of days in a given interval.
        Return a typical number, used for calculating bar widths, and other
        minor charts tweaks.
        """
        days_per_interval = {
            'yearly': 365,
            'quarterly': 91,
            'monthly': 30,
            'weekly': 7,
            'daily': 1,
        }
        return days_per_interval[interval]

    def _guess_interval(self):
        """ Return a probable interval, e.g. "montly", given current data
        """
        interval = "yearly"
        for serie in self.data:
            dates = [to_date(x[0]) for x in serie]
            years = [x.year for x in dates]
            months = [x.month for x in dates]
            yearmonths = [x[0][:7] for x in serie]
            weeks = [str(x.year) + str(x.isocalendar()[1]) for x in dates]
            if len(years) > len(set(years)):
                # there are years with more than one point
                if all(m in ["01", "04", "07", "10"] for m in months):
                    interval = "quarterly"
                else:
                    interval = "monthly"
                    if len(yearmonths) > len(set(yearmonths)):
                        interval = "weekly"
                    if len(weeks) > len(set(weeks)):
                        interval = "daily"
        return interval

    def _add_data(self):

        series = self.data
        # Select a date to highlight
        if self.highlight is not None:
            highlight_date = to_date(self.highlight)

        # Make an educated guess about the interval of the data
        if self.interval is None:
            self.interval = self._guess_interval()

        # Formatters for axis and annotations
        formatter = Formatter(self.language, scale="celsius")
        if self.units == "percent":
            y_formatter = FuncFormatter(formatter.percent)
            a_formatter = y_formatter
        elif self.units == "degrees":
            y_formatter = FuncFormatter(formatter.temperature_short)
            a_formatter = FuncFormatter(formatter.temperature)
        else:
            y_formatter = FuncFormatter(formatter.number)
            a_formatter = y_formatter

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
            # Use strong color for first series, if multiple
            if i == 0 and len(series) > 1:
                color = self.style["strong_color"]
            else:
                color = self.style["neutral_color"]

            values = [to_float(x[1]) for x in serie]
            dates = [to_date(x[0]) for x in serie]

            highlight_value = None
            if self.highlight:
                try:
                    highlight_value = values[dates.index(highlight_date)]
                    highlight_values.append(highlight_value)
                except ValueError:
                    # If this date is not in series, silently ignore
                    pass

            if self.highlight and highlight_value:
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

                if len(self.labels) > i:
                    line.set_label(self.labels[i])

                # add highlight marker
                if highlight_value:
                    self.ax.plot(highlight_date, highlight_value,
                                 c=color,
                                 marker='o',
                                 zorder=2)

            elif self.type == "bars":
                colors = []
                for timepoint in dates:
                    if highlight_value and timepoint == highlight_date:
                        colors.append(self.style["strong_color"])
                    else:
                        colors.append(self.style["neutral_color"])

                # Replace None values with 0's to be able to plot bars
                values = [0 if v is None else v for v in values]
                if self.interval is None:
                    # if no interval provided, self._guess_interval() somehow
                    # failed to come up with a proper estimate
                    bar_w = delta.days * 0.96 / self.len(self.data.x_points)
                else:
                    bar_w = self._days_in(self.interval) * 0.96

                bars = self.ax.bar(dates, values,
                                   color=colors,
                                   width=bar_w,
                                   zorder=2)

                if len(self.labels) > i:
                    bars.set_label(self.labels[i])

        # Annotate highlighted points/bars
        for hv in highlight_values:
            value_label = a_formatter(hv)
            xy = (highlight_date, hv)
            if hv == max(highlight_values):
                # Also used for single series, eg all bars charts
                self._annotate_point(value_label, xy, direction="up")
            elif hv == min(highlight_values):
                self._annotate_point(value_label, xy, direction="down")
            else:
                self._annotate_point(value_label, xy, direction="left")

        # Highlight diff
        y0, y1 = highlight_diff['y0'], highlight_diff['y1']
        # Only if more than one series has a value at this point, and they
        # actually look different
        if self.highlight and (len(highlight_values) > 1) and (a_formatter(y0) != a_formatter(y1)) and self.type == "line":
            self.ax.vlines(highlight_date, y0, y1,
                           colors=self.style["neutral_color"],
                           linestyles='dashed')
            diff = a_formatter(abs(y0-y1))
            xy = (highlight_date, (y0 + y1) / 2)
            self._annotate_point(diff, xy, direction="right")

        # Shade area between lines if there are exactly 2 series
        # For more series, the chart will get messy with shading
        if len(series) == 2:
            # Fill any gaps in series
            filled_values = self.data.filled_values
            self.ax.fill_between([to_date(x) for x in self.data.x_points],
                                 filled_values[0],  # converted to float already
                                 filled_values[1],
                                 facecolor=self.style["fill_between_color"],
                                 alpha=self.style["fill_between_alpha"])

        # Y axis formatting
        # TODO: Clea up this, and add proper handling to negative ymax cases
        padding_bottom = self.data.min_val * 0.15
        if self.ymin is not None:
            ymin = min(self.ymin, self.data.min_val - padding_bottom)
        else:
            ymin = self.data.min_val - padding_bottom
        self.ax.set_ylim(ymin=ymin,
                         ymax=self.data.max_val * 1.15)

        self.ax.yaxis.set_major_formatter(y_formatter)
        self.ax.yaxis.grid(True)

        # X ticks and formatter
        if delta.days > 365:
            ticks = get_year_ticks(xmin, xmax, max_ticks=self.max_ticks)
            self.ax.set_xticks(ticks)
            self.ax.xaxis.set_major_formatter(DateFormatter('%Y'))
        else:
            loc = get_best_locator(delta, len(dates))
            self.ax.xaxis.set_major_locator(loc)
            fmt = FuncFormatter(lambda x, pos:
                                Formatter(self.language).short_month(pos+1))
            self.ax.xaxis.set_major_formatter(fmt)

        # Add labels
        if len(self.labels):
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
                         color=self.style["strong_color"], zorder=4,
                         marker=marker, linestyle='dashed')

            # Annotate points in trendline
            for i, date in enumerate(dates):
                xy = (date, values[i])
                # TODO: find an algorithm for positioning this text
                if i < len(dates)-1:
                    if values[i] < values[i+1]:
                        dir = "down"
                    else:
                        dir = "up"
                else:
                    if values[i-1] < values[i]:
                        dir = "up"
                    else:
                        dir = "down"
                self._annotate_point(a_formatter(values[i]), xy,
                                     color=self.style["strong_color"],
                                     direction=dir)

            #from adjustText import adjust_text
            #x = [a.xy[0] for a in self._annotations]
            #y = [a.xy[1] for a in self._annotations]
            #adjust_text(self._annotations,
            #            x=x, y=y)
