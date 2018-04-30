""" Create charts and upload and store them as files.
For use with Newsworthy's robot writer and other similar projects.
"""
from os import environ
import os
from io import BytesIO
import yaml
from matplotlib.colors import to_rgba
from matplotlib import pyplot as plt
from matplotlib import rc_file, rcParams
from matplotlib.font_manager import FontProperties
from .mimetypes import MIME_TYPES
from .storage import LocalStorage

HERE = os.path.dirname(__file__)

# Define colors as rgba to be able to adjust opacity
NEUTRAL_COLOR = to_rgba("#999999", 1)
""" Default data color """
STRONG_COLOR = to_rgba("#5aa69d", 1)
""" Default color for highlighting """
EXTRA_STRONG_COLOR = to_rgba("#993333", 1)
""" Default color for e.g. highlighting elements in
    an already highlighted series """

image_formats = MIME_TYPES.keys()


class Chart(object):
    """ Encapsulates a matplotlib plt object
    """
    data = None
    # Use getter/setter because user can manipulate the fig title in more ways
    _title = None
    xlabel = None
    ylabel = None
    caption = None

    def __init__(self, width: int, height: int, storage=LocalStorage(),
                 size: str='normal', style: str='newsworthy',
                 strong_color: str=STRONG_COLOR):
        """
        :param width: width in pixels
        :param height: height in pixels
        :param size: 'normal'|'small', use small to increase size of elements
            if intended to display as mini chart.
        """

        self.storage = storage

        # Load default style
        # Dynamically loading them here allows us to provide alternate styles.
        style_file = os.path.join(HERE, 'rc', style)
        rc_file(style_file)

        # The style files may also contain an extra section with typography
        # for titles and captions (these can only be separately style in code,
        # as of Matplotlib 2.2)
        # This is a hack, but it's nice to have all styling in one file
        # The extra styling is prefixed with `#!`
        with open(style_file, 'r') as f:
            doc = f.readlines()
            rcParamsNewsworthy = "\n".join([d[2:]
                                           for d in doc if d.startswith("#!")])
        rcParamsNewsworthy = yaml.load(rcParamsNewsworthy)
        title_font = [x.strip()
                      for x in rcParamsNewsworthy["title_font"]
                      .split(",")]

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
        # w, h = plt.gcf().get_size_inches()

        self._fontsize = rcParams["font.size"]
        self.font = FontProperties()
        #fontsize = w * 2.2 * factor
        #self._fontsize = w * 2.2 * factor
        #self._fontsize_small = fontsize * 0.8
        #self._fontsize_title = fontsize * 1.4
        #self._linewidth = w * 0.4 * factor
        #self._markersize = 8.0 * factor
        #self.font.set_size(fontsize)

        # Dynamic typography
        self.font.set_family(rcParams["font.sans-serif"])

        self.small_font = self.font.copy()
        self.small_font.set_size("small")

        self.title_font = self.font.copy()
        self.title_font.set_family(title_font)
        self.title_font.set_size(rcParams["figure.titlesize"])

        # Customizable colors
        self._strong_color = to_rgba(strong_color, 1)

        self.fig, self.ax = plt.subplots()
        self.w, self.h = width, height

        # Calculate size in inches
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

        return self.plt.annotate(text, xy=xy, **opts)

    def _add_caption(self, caption):
        """ Adds a caption. Supports multiline input.
        """
        self.fig.text(0.01, 0.01, caption,
                      color=NEUTRAL_COLOR, wrap=True,
                      fontproperties=self.small_font)

        # Add some extra space
        n_caption_rows = len(caption.split("\n"))
        line_height = self._fontsize * 1.6 / float(self.h)
        offset = line_height * (3 + n_caption_rows)
        # And some further spacing if there is an axis label
        if self.xlabel is not None:
            # This amount is approximate
            offset += line_height * 2

        # If .tight_layout() is run after .subplots_adjust() changes will
        # be overwritten
        self.fig.subplots_adjust(bottom=offset)

    def _add_title(self, title_text):
        """ Adds a title """
        self.fig.suptitle(title_text, wrap=True,
                          multialignment="left",
                          fontproperties=self.title_font)
        self.fig.tight_layout()

    def _add_xlabel(self, label):
        """Adds a label to the x axis."""
        self.ax.set_xlabel(label, fontproperties=self.small_font)
        self.fig.tight_layout()

    def _add_ylabel(self, label):
        """Adds a label to the y axis."""
        self.ax.set_ylabel(label, fontproperties=self.small_font)
        self.fig.tight_layout()

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
            self._add_xlabel(self.xlabel)
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
        if self.fig._suptitle:
            return self.fig._suptitle.get_text()
        else:
            return str(id(self))

    def __repr__(self):
        # Use type(self).__name__ to get the right class name for sub classes
        return "<{cls}: {name} ({h} x {w})>".format(cls=type(self).__name__,
                                                    name=str(self),
                                                    w=self.w, h=self.h)
