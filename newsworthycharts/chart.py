""" Create charts and upload them the to Amazon S3. For use with Newsworthy's
robot writer and other similar projects.
"""
from os import environ
from io import BytesIO
from textwrap import wrap
# import matplotlib
# matplotlib.use('Agg')  # Set backend before further imports
# moved to matplotlibrc
from matplotlib.colors import to_rgba
from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties
from .mimetypes import MIME_TYPES
from .storage import LocalStorage

# Define colors as rgba to be able to adjust opacity
NEUTRAL_COLOR = to_rgba("#999999", 1)
""" Default data color """
STRONG_COLOR = to_rgba("#5aa69d", 1)
""" Default color for highlighting """
EXTRA_STRONG_COLOR = to_rgba("#993333", 1)
""" Default color for e.g. highlighting elements in
    an already highlighted series """

# Default typefacec
CONDENSED_FONT = ['Open Sans Condensed', 'Ubuntu Condensed']
REGULAR_FONT = ['Open Sans', 'Helvetica', 'Arial']

image_formats = MIME_TYPES.keys()

class Chart(object):
    """ Encapsulates a matplotlib plt object
    """
    def __init__(self, width: int, height: int, storage=LocalStorage(),
                 size: str='normal',
                 strong_color: str=STRONG_COLOR, rcParams: dict={}):
        """
        :param width: width in pixels
        :param height: height in pixels
        :param size: 'normal'|'small', use small to increase size of elements
            if intended to display as mini chart.
        :param strong_color (str): color used for highlights, preferably as HEX
        :param rcParams (dict): override defult rcParams
        :param s3_bucket (str): The name of an S3 bucket
        """

        self.s3_bucket = s3_bucket
        self.storage = storage

        # Styling
        # Style reference: https://matplotlib.org/users/customizing.html
        # When a chart is rendered as 'small' texts and elements
        # are enlarged
        factor = {
            "normal": 1.0,
            "small": 1.8
        }[size]
        self._factor = factor

        # Set size of chart
        # https://github.com/matplotlib/matplotlib/issues/2305/
        w, h = plt.gcf().get_size_inches()

        self.font = FontProperties()
        fontsize = w * 2.2 * factor
        self._fontsize = w * 2.2 * factor
        self._fontsize_small = fontsize * 0.8
        self._fontsize_title = fontsize * 1.4
        self._linewidth = w * 0.4 * factor
        self._markersize = 8.0 * factor
        self.font.set_size(fontsize)

        # Typography
        self._regular_font = REGULAR_FONT
        self.font.set_family(REGULAR_FONT)

        self.condensed_font = self.font.copy()
        self.small_font = self.font.copy()
        self.title_font = self.font.copy()
        self.condensed_font.set_family(CONDENSED_FONT)
        self.small_font.set_size(self._fontsize_small)
        self.title_font.set_size(self._fontsize_title)

        # Customizable colors
        self._strong_color = to_rgba(strong_color, 1)

        plt.rcParams['font.size'] = fontsize
        plt.rcParams['axes.titlesize'] = self._fontsize_title

        plt.rcParams['xtick.labelsize'] = self._fontsize_small
        plt.rcParams['ytick.labelsize'] = self._fontsize_small
        plt.rcParams['legend.fontsize'] = fontsize
        plt.rcParams['figure.titlesize'] = fontsize
        plt.rcParams['font.family'] = self._regular_font
        plt.rcParams['font.monospace'] = 'Ubuntu Mono'

        # Apply custom params
        plt.rcParams.update(rcParams)

        #self.fig = plt.figure()
        self.fig, self.ax = plt.subplots()
        self.w, self.h = width, height

        self._xlabel = None
        self._ylabel = None

        dpi = self.fig.get_dpi()
        real_width = float(width)/float(dpi)
        real_height = float(height)/float(dpi)
        self.fig.set_size_inches(real_width, real_height)

    def _annotate_point(self, text, xy, direction, **kwargs):
        """Adds a label to a given point.

        :param text: text content of label
        :param xy: coordinates to annotate
        :param direction: placement of annotation.
            ("up", "down", "left", "right")
        :param kwags: any params accepted by plt.annotate
        """
        opts = {
            "fontname": self._regular_font,
            "fontsize": self._fontsize,
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

        return self.plt.annotate(text, xy=xy, **opts)

    def _add_caption(self, caption):
        """ Adds a caption. Supports multiline input.

        `add_caption` should be executed _after_ `add_title`, `add_xlabel` and
        `add_ylabel.`
        """
        self.fig.figtext(0.01, 0.01, caption,
                         color=NEUTRAL_COLOR,
                         fontname=self._regular_font,
                         fontsize=self._fontsize_small)
        # Add some extra space to fit a two line caption
        n_caption_rows = len(caption.split("\n"))
        line_height = self._fontsize / float(self.h)
        offset = line_height * (4 + n_caption_rows)

        # And some further spacing if there is an axis label
        if self._xlabel is not None:
            # This amount is approximate
            offset += line_height * 2

        # If .tight_layout() is run after .subplots_adjust() changes will
        # be overwritten
        self.plt.subplots_adjust(bottom=offset)

    def _add_title(self, title):
        """ Adds a title """
        # Wrap title at a given number of chars
        # If the font family is changed wrap_at should be reviewed
        # Dynamic rescaling based on actual with seems difficult in matplotlib
        # This works pretty well.
        wrap_at = 50.0 / self._factor
        print("wrapping at {}".format(wrap_at))
        lines = wrap(title, wrap_at)  # split to list of lines
        print(lines)
        title_with_linebreaks = "\n".join(lines)
        title = self.fig.suptitle(title_with_linebreaks, wrap=True,
                                  horizontalalignment="left",
                                  fontproperties=self.title_font)

        # how many percent of height is the font title size?
        line_height = self._fontsize_title / float(self.h)

        # add some padding
        padd = 1 + line_height * 0.2
        title.set_y(padd)  # 1.1 would add 10% height
        self.fig.tight_layout()

    def _add_xlabel(self, label):
        """Adds a label to the x axis."""
        self.ax.set_xlabel(label, fontproperties=self.small_font,
                           labelpad=self._fontsize)

    def _add_ylabel(self, label):
        """Adds a label to the y axis."""
        self.ax.set_ylabel(label, fontproperties=self.small_font,
                           labelpad=self._fontsize)

    def _add_data(self):
        """ Add some data to the chart """
        pass

    def render(self, key, img_format):
        """
         Apply all changes, render file, and send to storage.
        """

        # Apply all changes, in the correct order for consistent rendering
        if self.data is not None:
            self._add_data(self.data)
        if self.title is not None:
            self._add_title(self.title)
        if self.ylabel is not None:
            self._add_ylabel(self.ylabel)
        if self.xlabel is not None:
            plt._add_xlabel(self.xlabel)
        if self.caption is not None:
            chart._add_caption(self.caption)

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

    @title.setter
    def title(self, t):
        self._title = t

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

    def __str__(self):
        # Return main title or id
        if self.fig._suptitle:
            return self.fig._suptitle.get_text()
        else:
            return str(id(self))

    def __repr__(self):
        # Use type(self).__name__ to get the right class name for sub classes
        return "<{cls}: {name} ({h} x {w})>".format(cls=type(self).__name__,
                                                    name=str(self),
                                                    w=self.w, h=self.h)
