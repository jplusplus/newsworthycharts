""" Create charts and upload and store them as files.
For use with Newsworthy's robot writer and other similar projects.
"""
from io import BytesIO
from math import inf
from matplotlib.font_manager import FontProperties
from .utils import loadstyle, rpad, to_float, to_date
from .mimetypes import MIME_TYPES
from .storage import LocalStorage
from .formatter import Formatter
from .locator import get_best_locator, get_year_ticks
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import DateFormatter
from langcodes import standardize_tag
from datetime import datetime

image_formats = MIME_TYPES.keys()


class Chart(object):
    """ Convenience wrapper around a Matplotlib figure
    """
    # Use getter/setter for title as user might manipulate it though .fig
    _title = None
    xlabel = None
    ylabel = None
    caption = None
    highlight = None
    annotations = []
    data = []  # A list of datasets
    labels = []  # Optionally one label for each dataset
    # TODO: Create custom list classes: https://stackoverflow.com/questions/3487434/overriding-append-method-after-inheriting-from-a-python-list#3488283

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

    def _annotate_point(self, text, xy, direction, **kwargs):
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
        offset = 10  # px between point and text
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

        return self.ax.annotate(text, xy=xy, **opts)

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
        self._add_data(self.data)
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

    _units = "count"
    _type = "bars"
    ymin = 0
    max_ticks = 5

    @property
    def units(self):
        return self._units

    @units.setter
    def units(self, val):
        if val in ["count", "percent"]:
            self._units = val
        else:
            raise ValueError("Supported units are count and percent")

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, val):
        if val in ["bars", "line"]:
            self._type = val
        else:
            raise ValueError("Supported types are bars and line")

    def _add_data(self, series):

        # Select a date to highlight
        if self.highlight is not None:
            highlight_date = to_date(self.highlight)
        else:
            # Use last date. max works well on ISO date strings
            highlight_date = to_date(max([x[-1][0] for x in series]))

        # Make sure there are as many labels as series
        self.labels = rpad(self.labels, None, len(series))

        # Store y values while we are looping the data, to adjust axis,
        # and highlight diff
        ymax = 0
        ymin = self.ymin
        xmin = datetime.max
        xmax = datetime.min
        highlight_diff = {
            'y0': inf,
            'y1': -inf
        }
        for i, serie in enumerate(series):
            values = [to_float(x[1]) for x in serie]
            dates = [to_date(x[0]) for x in serie]

            try:
                highlight_value = values[dates.index(highlight_date)]
            except ValueError:
                # If this date is not in series, silently ignore
                highlight_value = None

            xmax = max(xmax, max(dates))
            xmin = min(xmin, min(dates))
            ymax = max(ymax, max([x for x in values if x is not None]))
            ymin = min(ymin, min([x for x in values if x is not None]))
            if highlight_value:
                highlight_diff['y0'] = min(highlight_diff['y0'],
                                           highlight_value)
                highlight_diff['y1'] = max(highlight_diff['y1'],
                                           highlight_value)

            if self.type == "line":
                line, = self.ax.plot(dates, values,
                                     color=self.style["neutral_color"],
                                     zorder=2)

                if self.labels[i]:
                    line.set_label(self.labels[i])

                # highlight
                if highlight_value:
                    self.ax.plot(highlight_date, highlight_value,
                                 c=self.style["strong_color"],
                                 marker='o',
                                 zorder=2)

            elif self.type == "bars":
                colors = []
                for timepoint in dates:
                    if timepoint == highlight_date:
                        colors.append(self.style["strong_color"])
                    else:
                        colors.append(self.style["neutral_color"])

                # Replace None values with 0's to be able to plot bars
                values = [0 if v is None else v for v in values]
                bars = self.ax.bar(dates, values,
                                   color=colors,
                                   width=320,  # FIXME use (delta.unit / ticks)
                                   zorder=2)

                if self.labels[i]:
                    bars.set_label(self.labels[i])

        # Adjust y axis to data range
        self.ax.set_ylim(ymin=ymin, ymax=ymax*1.15)

        # Y formatter
        if self.units == "percent":
            y_formatter = FuncFormatter(Formatter(self.language).percent)
        else:
            y_formatter = FuncFormatter(Formatter(self.language).number)
        self.ax.yaxis.set_major_formatter(y_formatter)

        # Grid
        self.ax.yaxis.grid(True)

        # FIXME: Use all dates, this is just a leftover from last serie
        delta = xmax - xmin
        # X ticks and formatter
        if delta.days > 365:
            ticks = get_year_ticks(dates, max_ticks=self.max_ticks)
            self.ax.set_xticks(ticks)
            self.ax.xaxis.set_major_formatter(DateFormatter('%Y'))
        else:
            loc = get_best_locator(delta, len(dates))
            self.ax.xaxis.set_major_locator(loc)
            fmt = FuncFormatter(lambda x, pos:
                                Formatter(self.language).short_month(pos+1))
            self.ax.xaxis.set_major_formatter(fmt)

        # Highlight point
        if highlight_value:
            value_label = y_formatter(highlight_value)
            xy = (highlight_date, highlight_value)
            self._annotate_point(value_label, xy, direction="right")  # FIXME dir

        # Trend line
        """
        # Add highlight_change trend line
        if args.highlight_change and i == 0:
            changedates = [datetime.strptime(x, "%Y-%m-%d") for x in literal_eval(args.highlight_change)]
            changedata = [data[dates.index(d)] for d in changedates]
            line, = ax.plot(changedates, changedata,
                             color=highlight_color, zorder=4, marker='o',
                             linestyle='dashed')
        """
