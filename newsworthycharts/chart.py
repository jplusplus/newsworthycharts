""" Create charts and upload and store them as files.
For use with Newsworthy's robot writer and other similar projects.
"""
from io import BytesIO
from matplotlib.font_manager import FontProperties
from .utils import loadstyle
from .mimetypes import MIME_TYPES
from .storage import LocalStorage
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

image_formats = MIME_TYPES.keys()


class Chart(object):
    """ Convenience wrapper around a Matplotlib figure
    """
    data = None
    # Use getter/setter for title as user might manipulate it though .fig
    _title = None
    xlabel = None
    ylabel = None
    caption = None
    annotations = []

    def __init__(self, width: int, height: int, storage=LocalStorage(),
                 style: str='newsworthy'):
        """
        :param width: width in pixels
        :param height: height in pixels
        :param storage: storage object that will handle file saving. Default
                        LocalStorage() class will save a file the working dir.
        :param style: a predefined style or the path to a custom style file
        """

        self.storage = storage
        self.w, self.h = width, height
        self.style = loadstyle(style)

        # Dynamic typography
        self.font = FontProperties()

        self.small_font = self.font.copy()
        self.small_font.set_size("small")

        self.title_font = self.font.copy()
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
        # We need to draw the text first, to know its dimensions
        self.fig.draw(renderer=self.fig.canvas.renderer)
        bbox = text.get_window_extent()
        margin = self.style["figure.subplot.bottom"]
        margin += bbox.height / float(self.h)
        self.fig.subplots_adjust(bottom=margin)

    def _add_title(self, title_text):
        """ Adds a title """
        self.fig.suptitle(title_text, wrap=True,
                          multialignment="left",
                          fontproperties=self.title_font)

    def _add_xlabel(self, label):
        """Adds a label to the x axis."""
        self.ax.set_xlabel(label, fontproperties=self.small_font)

    def _add_ylabel(self, label):
        """Adds a label to the y axis."""
        self.ax.set_ylabel(label, fontproperties=self.small_font)

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
        for a in self.annotations:
            self._annotate_point(a["text"], a["xy"], a["direction"])
        if self.title is not None:
            self._add_title(self.title)
        if self.ylabel is not None:
            self._add_ylabel(self.ylabel)
        if self.xlabel is not None:
            self._add_xlabel(self.xlabel)
        # tight_layout after _add_caption would ruin extra padding added there
        self.fig.tight_layout()
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
