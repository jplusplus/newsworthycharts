""" Create charts and upload them the to Amazon S3. For use with Newsworthy's
robot writer and other similar projects.
"""
from os import environ
from io import BytesIO
from textwrap import wrap
import boto3
# import matplotlib
# matplotlib.use('Agg')  # Set backend before further imports
# moved to matplotlibrc
from matplotlib.colors import to_rgba
from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties

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

# This also serves as list of available output formats
MIME_TYPES = {
    'png': "image/png",
    'svg': "image/svg+xml",
    'eps': "application/postscript"
}


class AmazonError(Exception):
    """ Error connecting or uploading to Amazon S3 """
    pass


class Chart(object):
    """ Encapsulates a matplotlib plt object
    """

    def __init__(self, width: int, height: int, size: str='normal',
                 strong_color: str=STRONG_COLOR, rcParams: dict={},
                 s3_bucket: str=environ.get("S3_BUCKET")):
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
        self.font = FontProperties()

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
        self.condensed_font.set_family(CONDENSED_FONT)

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

        self.fig = plt.figure()
        self.fig, self.ax = plt.subplots()
        self.w, self.h = width, height

        self._xlabel = None
        self._ylabel = None

        dpi = self.fig.get_dpi()
        real_width = float(width)/float(dpi)
        real_height = float(height)/float(dpi)
        self.fig.set_size_inches(real_width, real_height)

    def annotate_point(self, text, xy, direction, **kwargs):
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

    def add_caption(self, caption):
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

    def add_title(self, title):
        """ Adds a title """
        # Wrap title at a given number of chars
        # If the font family is changed wrap_at should be reviewed
        # Dynamic rescaling based on actual with seems difficult in matplotlib
        # This works pretty well.
        wrap_at = 50.0 / self._factor
        lines = wrap(title, wrap_at)  # split to list of lines
        title_with_linebreaks = "\n".join(lines)
        title = self.fig.suptitle(title_with_linebreaks, wrap=True,
                                  horizontalalignment="left",
                                  fontproperties=self.condensed_font)

        # how many percent of height is the font title size?
        line_height = self._fontsize_title / float(self.h)

        # add some padding
        padd = 1 + line_height * .2
        title.set_y(padd)  # 1.1 would add 10% height
        self.fig.tight_layout()

    def add_xlabel(self, label):
        """Adds a label to the x axis."""
        self._xlabel = self.plt.xlabel(label, fontname=self._regular_font,
                                       fontsize=self._fontsize_small, labelpad=self._fontsize)

    def add_ylabel(self, label):
        """Adds a label to the y axis."""
        self._ylabel = self.plt.ylabel(label, fontname=self._regular_font,
                                       fontsize=self._fontsize_small, labelpad=self._fontsize)

    def render(self, key, img_format):
        """
         Save an image file from the plot object to Amazon S3.
        """
        if environ.get("ENV") == "development":
            self.plt.savefig("test.%s" % img_format, format=img_format)
        # Save plot in memory, to write it directly to S3
        buf = BytesIO()
        self.plt.savefig(buf, format=img_format)
        buf.seek(0)

        filename = key + "." + img_format
        mime_type = MIME_TYPES[img_format]
        try:
            s3_client = boto3.resource('s3')
            bucket = s3_client.Bucket(self.s3_bucket)
            bucket.put_object(Key=filename, Body=buf,
                              ACL='public-read', ContentType=mime_type)
        except Exception:
            raise AmazonError

    def render_all(self, key):
        """
        Render all available formats
        """
        for file_format in MIME_TYPES.keys():
            self.render(key, file_format)

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
