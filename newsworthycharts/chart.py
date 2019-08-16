""" Create charts and store them as images.
For use with Newsworthy's robot writer and other similar projects.
"""
from .lib import color_fn
from .lib.mimetypes import MIME_TYPES
from .lib.utils import loadstyle
from .lib.formatter import Formatter
from .lib.datalist import DataList
from .storage import LocalStorage

from io import BytesIO
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from langcodes import standardize_tag
from PIL import Image
from babel import Locale

image_formats = MIME_TYPES.keys()


class Chart(object):
    """ Convenience wrapper around a Matplotlib figure
    """

    def __init__(self, width: int, height: int, storage=LocalStorage(),
                 style: str='newsworthy', language: str='en-GB', *args, **kwargs):
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
        if "color_fn" in kwargs:
            self.color_fn = kwargs.get("color_fn")
        else:
            self.color_fn = None
        # Custom coloring function

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

    def _color_by(self, *args, **kwargs):
        """Color by some rule.
        Role of args and and kwargs are determined by the color rule.
        """
        color_name = None
        rule = self.color_fn
        if rule == "positive_negative":
            value = args[0]
            color_name = color_fn.positive_negative(value)
        else:
            raise ValueError("Unknown color rule: {}".format(rule))

        if color_name in ["strong", "neutral", "positive", "negative"]:
            c = self.style[color_name + "_color"]
        else:
            c = color_name
        return c

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
