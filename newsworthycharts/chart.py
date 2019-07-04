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
from dateutil.relativedelta import relativedelta
from PIL import Image
from babel import Locale

image_formats = MIME_TYPES.keys()


class Chart(object):
    """ Convenience wrapper around a Matplotlib figure
    """

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

        # Properties of this class member
        # The user can alter these at any time
        self.data = DataList()  # A list of datasets
        self.annotate_trend = True  # Print out values at points on trendline?
        self.trendline = []  # List of x positions, or data points
        self.labels = []  # Optionally one label for each dataset
        self.annotations = []  # Manually added annotations
        self.interval = None  # yearly|quarterly|monthly|weekly|daily
        # We will try to guess interval based on the data,
        # but explicitly providing a value is safer. Used for finetuning.
        self.show_ticks = True  # toggle category names, dates, etc
        self.xlabel = None
        self.ylabel = None
        self.caption = None
        self.highlight = None
        self.decimals = None
        # number of decimals to show in annotations, value ticks, etc
        # None means automatically chose the best number
        self.logo = None
        # Path to image that will be embedded in the caption area
        # Can also be set though a style property

        # Properties managed through getters/setters
        self._title = None
        self._units = "count"

        # Calculated properties
        self._annotations = []  # Automatically added annotations
        self.storage = storage
        self.w, self.h = int(width), int(height)
        self.style = loadstyle(style)
        # Standardize and check if language tag is a valid BCP 47 tag
        self.language = standardize_tag(language)
        self.locale = Locale.parse(self.language.replace("-", "_"))

        # Dynamic typography
        self.title_font = FontProperties()
        self.title_font.set_family(self.style["title_font"])
        self.title_font.set_size(self.style["figure.titlesize"])
        self.title_font.set_weight(self.style["figure.titleweight"])

        # By default no decimals if unit is “count”
        if self.decimals is None and self._units == "count":
            self.decimals = 0

        self.fig = Figure()
        FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        # self.fig, self.ax = plt.subplots()
        self.value_axis = self.ax.yaxis
        self.category_axis = self.ax.xaxis

        # Calculate size in inches
        self._set_size(width, height)

    def _set_size(self, w, h=None):
        """ Set figure size, in pixels """
        dpi = self.fig.get_dpi()
        real_width = float(w)/dpi
        if h is None:
            real_height = self.fig.get_figheight()
        else:
            real_height = float(h)/dpi
        self.fig.set_size_inches(real_width, real_height)

    def _get_value_axis_formatter(self):
            formatter = Formatter(self.language,
                                  decimals=self.decimals,
                                  scale="celsius")
            if self.units == "percent":
                return FuncFormatter(formatter.percent)
            elif self.units == "degrees":
                return FuncFormatter(formatter.temperature_short)
            else:
                return FuncFormatter(formatter.number)

    def _get_annotation_formatter(self):
            formatter = Formatter(self.language,
                                  decimals=self.decimals,
                                  scale="celsius")
            if self.units == "percent":
                return FuncFormatter(formatter.percent)
            elif self.units == "degrees":
                return FuncFormatter(formatter.temperature)
            else:
                return FuncFormatter(formatter.number)

    def _text_rel_height(self, obj):
        """ Get the relative height of a text object to the whole canvas.
        Will try and guess even if wrap=True.
        """
        if not obj.get_wrap():
            # No autowrapping, use default bbox checking
            return self._rel_height(obj)

        self.fig.canvas.draw()  # Draw text to find out how big it is
        t = obj.get_text()
        r = self.fig.canvas.renderer
        w, h, d = r.get_text_width_height_descent(t, obj._fontproperties,
                                                  ismath=False)
        num_lines = len(obj._get_wrapped_text().split("\n"))
        return (h * num_lines) / float(self.h)

    def _rel_height(self, obj):
        """ Get the relative height of a chart object to the whole canvas.
        """
        self.fig.canvas.draw()  # We must draw the canvas to know all sizes
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
            #  'fontsize': "small",
            "textcoords": "offset pixels",
        }

        offset = round(self.style["font.size"] * 0.8)
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

    def _add_caption(self, caption, hextent=None):
        """ Adds a caption. Supports multiline input.
            hextent is the left/right extent,  e.g. to avoid overlapping a logo
        """
        # Wrap=true is hardcoded to use the extent of the whole figure
        # Our workaround is to resize the figure, draw the text to find the
        # linebreaks, and then restore the original width!
        if hextent is None:
            hextent = (0, self.w)
        self._set_size(hextent[1]-hextent[0])
        x1 = hextent[0] / self.w
        text = self.fig.text(x1 + 0.01, 0.01, caption,
                             color=self.style["neutral_color"], wrap=True,
                             fontsize="small")
        self.fig.canvas.draw()
        wrapped_text = text._get_wrapped_text()
        text.set_text(wrapped_text)
        self._set_size(self.w)

        # Increase the bottom padding by the height of the text bbox
        margin = self.style["figure.subplot.bottom"]
        margin += self._text_rel_height(text)
        self.fig.subplots_adjust(bottom=margin)

    def _add_title(self, title_text):
        """ Adds a title """
        # Get the position for the yaxis, and align title with it
        title_text += "\n"  # Ugly but efficient way to add 1em padding
        text = self.fig.suptitle(title_text, wrap=True, x=0,
                                 horizontalalignment="left",
                                 multialignment="left",
                                 fontproperties=self.title_font)

        # Increase the top padding by the height of the text bbox
        # Ignoring self.style["figure.subplot.top"]
        margin = 1 - self._text_rel_height(text)
        self.fig.subplots_adjust(top=margin)

    def _add_xlabel(self, label):
        """Adds a label to the x axis."""
        self.ax.set_xlabel(label, fontsize="small")

    def _add_ylabel(self, label):
        """Adds a label to the y axis."""
        self.ax.set_ylabel(label, fontsize="small")

    def _add_data(self):
        """ Plot data to the chart.
        Typically defined by a more specific subclass
        """
        raise NotImplementedError("This method should be overridden")

    def _apply_changes_before_rendering(self):
        """
         To ensure consistent rendering, we call this method just before
         rendering file(s). This is where all properties are applied.
        """
        # Apply all changes, in the correct order for consistent rendering
        self.fig.tight_layout()
        if len(self.data):
            self._add_data()
        if not self.show_ticks:
            self.category_axis.set_visible(False)
        else:
            # Remove dublicated labels (typically a side effect of using
            # few decimals while having a lot of values in a small range)
            pass
            """
            self.fig.canvas.draw()
            tl = [x.get_text() for x in self.value_axis.get_ticklabels()]
            print(tl)
            tl = [x if tl[i-1] != x else "" for (i, x) in enumerate(tl)]
            print(tl)
            self.value_axis.set_ticklabels(tl)
            """

        for a in self.annotations:
            self._annotate_point(a["text"], a["xy"], a["direction"])
        if self.ylabel is not None:
            self._add_ylabel(self.ylabel)
        if self.xlabel is not None:
            self._add_xlabel(self.xlabel)
        if self.title is not None:
            self._add_title(self.title)
        logo = self.style.get("logo", self.logo)
        caption_hextent = None  # set this if adding a logo
        if logo:
            im = Image.open(logo)
            # scale down image if needed to fit
            new_width = min(self.w, im.size[0])
            new_height = new_width * (im.size[1] / im.size[0])
            im.thumbnail((new_width, new_height), Image.ANTIALIAS)

            # Position
            if self.locale.text_direction == "rtl":
                logo_im = self.fig.figimage(im, 0, 0)
                ext = logo_im.get_extent()
                caption_hextent=(ext[1], self.w)
            else:
                logo_im = self.fig.figimage(im, self.w - im.size[0], 0)
                ext = logo_im.get_extent()
                caption_hextent=(0, ext[0])

        if self.caption is not None:
            # Add caption without image
            self._add_caption(self.caption, hextent=caption_hextent)

    def render(self, key, img_format):
        """
         render file, and send to storage.
        """
        # Apply all changes, in the correct order for consistent rendering
        self._apply_changes_before_rendering()

        # Save plot in memory, to write it directly to storage
        buf = BytesIO()
        self.fig.savefig(buf, format=img_format)
        buf.seek(0)
        self.storage.save(key, buf, img_format)

    def render_all(self, key):
        """
        Render all available formats
        """
        # Apply all changes, in the correct order for consistent rendering
        self._apply_changes_before_rendering()

        for file_format in image_formats:
            # Save plot in memory, to write it directly to storage
            buf = BytesIO()
            self.fig.savefig(buf, format=file_format)
            buf.seek(0)
            self.storage.save(key, buf, file_format)

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

    def __init__(self, *args, **kwargs):
        super(SerialChart, self).__init__(*args, **kwargs)
        self._type = "bars"
        self.bar_width = 0.9
        # Percent of period. 0.85 means a bar in a chart with yearly data will
        # be around 310 or 311 days wide.
        self.max_ticks = 5
        self._ymin = None

    @property
    def ymin(self):
        # WIP
        return self._ymin

    @ymin.setter
    def ymin(self, val):
        self._ymin = val

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
        """ Return number of days in a given period.
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
                    (d + relativedelta(years=1)).replace(day=1, month=1)
                    - d.replace(day=1, month=1)
                ).days
            elif interval == "quarterly":
                return (
                    (d + relativedelta(months=3)).replace(day=1)
                    - d.replace(day=1)
                ).days
            elif interval == "monthly":
                return (
                    (d + relativedelta(months=1)).replace(day=1)
                    - d.replace(day=1)
                ).days
            elif interval == "weekly":
                # Assuming ISO 8601 here
                return 7
            elif interval == "daily":
                return 1

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
        if val == max(values[index-1:index+2]):
            return "up"
        if val == min(values[index-1:index+2]):
            return "down"
        return "up"

    def _add_data(self):

        series = self.data
        # Select a date to highlight
        if self.highlight is not None:
            highlight_date = to_date(self.highlight)

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
                # Add single, orphaned data points as markers
                # None, 1, None, 1, 1, 1 =>  . ---
                l = len(values)
                if l == 1:
                    self.ax.plot(dates[0], values[0],
                                 c=color,
                                 marker='.',
                                 zorder=2)
                elif l > 1:
                    for j, v in enumerate(values):
                        plot_me = False
                        if v is not None:
                            if j == 0 and (values[j+1] is None):
                                plot_me = True
                            elif j == l-1 and (values[j-1] is None):
                                plot_me = True
                            elif (values[j-1] is None) and (values[j+1] is None):
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
                if self.highlight:
                    colors = []
                    for timepoint in dates:
                        if highlight_value and timepoint == highlight_date:
                            colors.append(self.style["strong_color"])
                        else:
                            colors.append(self.style["neutral_color"])
                else:
                    # use strong color if there is no highlight
                    colors = [self.style["strong_color"]] * len(dates)

                # Replace None values with 0's to be able to plot bars
                values = [0 if v is None else v for v in values]

                # Set bar width, based on interval
                bar_lengths = [self._days_in(self.interval, d) for d in dates]
                bar_widths = [l * self.bar_width for l in bar_lengths]

                # If there are too many ticks per pixel,
                # don't put whitespace betw bars. Make widths = 1
                bbox = self.ax.get_window_extent()
                if (sum(bar_widths) * 2 / len(dates)) > bbox.width:
                    bar_widths = [l * 1 for l in bar_lengths]

                bars = self.ax.bar(dates, values,
                                   color=colors,
                                   width=bar_widths,
                                   zorder=2)

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
            self.ax.axhline()

        # Highlight diff
        y0, y1 = highlight_diff['y0'], highlight_diff['y1']
        # Only if more than one series has a value at this point, and they
        # actually look different
        if self.highlight and\
           (len(highlight_values) > 1) and\
           (a_formatter(y0) != a_formatter(y1)) and\
           self.type == "line":

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
            min_x = self.data.inner_min_x
            max_x = self.data.inner_max_x
            self.ax.fill_between([to_date(x) for x in self.data.x_points],
                                 filled_values[0],  # already a float1w
                                 filled_values[1],
                                 where=[(x >= min_x and x <= max_x)
                                            for x in self.data.x_points],
                                 facecolor=self.style["fill_between_color"],
                                 alpha=self.style["fill_between_alpha"])

        # Y axis formatting
        padding_bottom = abs(self.data.min_val * 0.15)
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
            if self.annotate_trend:
                for i, date in enumerate(dates):
                    xy = (date, values[i])
                    dir = self._get_annotation_direction(i, values)
                    self._annotate_point(a_formatter(values[i]), xy,
                                         color=self.style["strong_color"],
                                         direction=dir)

            # from adjustText import adjust_text
            # x = [a.xy[0] for a in self._annotations]
            # y = [a.xy[1] for a in self._annotations]
            # adjust_text(self._annotations,
            #             x=x, y=y)


class CategoricalChart(Chart):
    """ Plot categorical data to a bar chart
    """

    def __init__(self, *args, **kwargs):
        super(CategoricalChart, self).__init__(*args, **kwargs)
        self._bar_orientation = "horizontal"  # [horizontal|vertical]

    @property
    def bar_orientation(self):
        return self._bar_orientation

    @bar_orientation.setter
    def bar_orientation(self, val):
        if val in ["horizontal", "vertical"]:
            self._bar_orientation = val
        else:
            raise ValueError("Valid oriantations: horizontal | vertical")

    def _add_data(self):
        if self.bar_orientation == "horizontal":
            self.value_axis = self.ax.xaxis
            self.category_axis = self.ax.yaxis

        a_formatter = self._get_annotation_formatter()
        va_formatter = self._get_value_axis_formatter()
        self.value_axis.set_major_formatter(va_formatter)
        self.value_axis.grid(True)

        for data in self.data:

            # Replace None values with 0's to be able to plot bars
            values = [0 if x[1] is None else float(x[1]) for x in data]
            categories = [x[0] for x in data]

            color = self.style["neutral_color"]
            highlight_color = self.style["strong_color"]

            if self.highlight is None:
                # use strong color if there is nothing to highlight
                colors = [highlight_color] * len(values)
            else:
                colors = [color] * len(values)

            # Add any annotations given inside the data
            # and also annotate highlighted value
            for i, d in enumerate(data):
                if d[1] is None:
                    # Dont annotate None values
                    continue
                # Get position for any highlighting to happen
                if self.bar_orientation == "horizontal":
                    xy = (d[1], i)
                    if d[1] >= 0:
                        dir = "right"
                    else:
                        dir = "left"
                else:
                    xy = (i, d[1])
                    if d[1] >= 0:
                        dir = "up"
                    else:
                        dir = "down"

                if d[2] is not None:
                    self._annotate_point(d[2], xy, direction=dir)
                elif self.highlight is not None and self.highlight == d[0]:
                    # Only add highlight value if not already annotated
                    self._annotate_point(a_formatter(d[1]), xy, direction=dir)

                if self.highlight is not None and self.highlight == d[0]:
                    colors[i] = highlight_color

            import numpy
            label_pos = numpy.arange(len(values))
            if self.bar_orientation == "horizontal":
                self.ax.barh(label_pos, values, align='center',
                             color=colors, zorder=2)
                self.ax.set_yticks(label_pos)
                self.ax.set_yticklabels(categories, fontsize='small')
                self.ax.invert_yaxis()

                # Make sure labels are not cropped
                yaxis_bbox = self.ax.yaxis.get_tightbbox(self.fig.canvas.renderer)
                margin = self.style["figure.subplot.left"]
                margin -= yaxis_bbox.min[0] / float(self.w)
                self.fig.subplots_adjust(left=margin)
            else:
                self.ax.bar(label_pos, values, color=colors, zorder=2)
                self.ax.set_xticks(label_pos)
                self.ax.set_xticklabels(categories, fontsize='small')
                self.ax.xaxis.set_ticks_position('none')
