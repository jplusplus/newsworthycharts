""" Create charts and store them as images.
For use with Newsworthy's robot writer and other similar projects.
"""
import types
from .lib import color_fn
from .lib.mimetypes import MIME_TYPES
from .lib.utils import loadstyle, outline, to_date

from .lib.formatter import Formatter
from .lib.datalist import DataList, DataSet
from .lib.locator import get_best_locator, get_year_ticks
from .storage import Storage, LocalStorage

from io import BytesIO
from matplotlib.path import Path
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import DateFormatter, num2date
from langcodes import standardize_tag
from PIL import Image
from babel import Locale
import warnings
from . import __version__


class Chart(object):
    """ Convenience wrapper around a Matplotlib figure
    """

    file_types = MIME_TYPES.keys()
    _uses_categorical_data = None

    def __init__(self, width: int, height: int, storage: Storage=LocalStorage(),
                 style: str='newsworthy', language: str='en-GB'):
        """
        :param width: width in pixels
        :param height: height in pixels
        :param storage: storage object that will handle file saving. Default
                        LocalStorage() class will save a file the working dir.
        :param style: a predefined style or the path to a custom style file
        :param language: a BCP 47 language tag (eg `en`, `sv-FI`)
        """

        # P U B L I C   P R O P E R T I E S
        # The user can alter these at any time
        self.data = DataSet() if self._uses_categorical_data else DataList()  # A list of datasets
        self.annotate_trend = True  # Print out values at points on trendline?
        self.trendline = []  # List of x positions, or data points
        self.labels = []  # Optionally one label for each dataset
        self.legend_title = None  # Experimental
        self.annotations = []  # Manually added annotations
        self.interval = None  # yearly|quarterly|monthly|weekly|daily
        # We will try to guess interval based on the data,
        # but explicitly providing a value is safer. Used for finetuning.
        self.show_ticks = True  # toggle category names, dates, etc
        self.subtitle = None
        self.note = None
        self.xlabel = None
        self.ylabel = None
        self.caption = None
        self.highlight = None
        self.highlight_annotation = True
        self.decimals = None
        self.yline = None
        self.type = None
        # number of decimals to show in annotations, value ticks, etc
        # None means automatically chose the best number
        self.force_decimals = False
        # Should we print ”1.0”, rather than ”1” in labels, annotations, etc
        self.logo = None
        # Path to image that will be embedded in the caption area
        # Can also be set though a style property
        self.color_fn = None
        # Custom coloring function

        # P R I V A T E   P R O P E R T I E S
        # Properties managed through getters/setters
        self._title = None
        self._units = "number"

        # Calculated properties
        self._annotations = []  # Automatically added annotations
        self._storage = storage
        self._style, self._nwc_style = loadstyle(style)
        # if len(self._nwc_style.keys()):
        #    warnings.warn("Using custom NWCharts settings in rc files is deprecated.")
        # Standardize and check if language tag is a valid BCP 47 tag
        self._language = standardize_tag(language)
        self._locale = Locale.parse(self._language.replace("-", "_"))

        # Dynamic typography
        self._title_font = FontProperties()
        self._title_font.set_family(self._nwc_style["title_font"])
        self._title_font.set_size(self._style["figure.titlesize"])
        self._title_font.set_weight(self._style["figure.titleweight"])

        self._fig = Figure(layout="tight")
        FigureCanvas(self._fig)
        self.ax = self._fig.add_subplot(111)
        # self._fig, self.ax = plt.subplots()
        self.value_axis = self.ax.yaxis
        self.category_axis = self.ax.xaxis

        # Calculate size in inches
        # Deferred from 1.46.0 to allow charts to override height!
        # self._set_size(width, height)
        self.requested_width, self.requested_height = width, height
        self._w = int(width)
        if height:
            self._h = int(height)

        # Chart elements. Made available for fitting.
        self._title_elem = None
        self._subtitle_elem = None
        self._note_elem = None
        self._caption_elem = None
        self._logo_elem = None

    def _get_height(self, w):
        """ This can be overridden by chart classes to provide optimal ratios """
        # Default to 1:1
        return w

    def _set_size(self, w, h=None):
        """ Set figure size, in pixels """
        dpi = self._fig.get_dpi()
        real_width = float(w) / dpi
        if h is None:
            real_height = self._fig.get_figheight()
        else:
            real_height = float(h) / dpi
        self._fig.set_size_inches(real_width, real_height)

    def _get_value_axis_formatter(self):
        return self._get_formatter(self.units)

    def _get_formatter(self, units):
        formatter = Formatter(self._language,
                              decimals=self.decimals,
                              force_decimals=self.force_decimals,
                              scale="celsius")
        if units == "percent":
            return FuncFormatter(formatter.percent)
        elif units == "degrees":
            return FuncFormatter(formatter.temperature_short)
        else:
            return FuncFormatter(formatter.number)

    def _get_annotation_formatter(self):
        return self._get_formatter(self.units)

    def _text_rel_height(self, obj):
        """ Get the relative height of a text object to the whole canvas.
        Will try and guess even if wrap=True.
        """
        if not obj.get_wrap():
            # No autowrapping, use default bbox checking
            return self._rel_height(obj)

        self._fig.canvas.draw()  # Draw text to find out how big it is
        t = obj.get_text()
        r = self._fig.canvas.get_renderer()
        # Get real line height
        w, h, d = r.get_text_width_height_descent(
            t.replace("\n", ""),  # avoid warning
            obj._fontproperties,
            ismath=False,
        )
        num_lines = len(obj._get_wrapped_text().split("\n"))
        return (h * (num_lines * 1.4)) / float(self._h)  # 1.4 is the line spacing used everywhere

    def _rel_height(self, obj):
        """ Get the relative height of a chart object to the whole canvas.
        """
        self._fig.canvas.draw()  # We must draw the canvas to know all sizes
        bbox = obj.get_window_extent()
        return bbox.height / float(self._h)

    def _color_by(self, *args, **kwargs):
        """Color by some rule.
        Role of args and and kwargs are determined by the color rule.
        """
        color_name = None
        rule = self.color_fn
        value = args[0]
        if isinstance(rule, types.LambdaType):
            color_name = rule(value)
        elif rule == "positive_negative":
            color_name = color_fn.positive_negative(value)
        elif rule == "warm_cold":
            color_name = color_fn.warm_cold(value, **kwargs)
        else:
            raise ValueError("Unknown color rule: {}".format(rule))

        if color_name in ["strong", "neutral", "positive", "negative", "warm", "cold"]:
            c = self._nwc_style[color_name + "_color"]
        else:
            c = color_name
        return c

    def _annotate_point(self, text, xy,
                        direction, offset=12,
                        **kwargs):
        """Add a label to a given point.

        :param text: text content of label
        :param xy: coordinates to annotate
        :param direction: placement of annotation.
            ("up", "down", "left", "right")
        :param kwags: any params accepted by plt.annotate
        """
        # TODO: Offset should maybe rather be a function of the font size,
        # but then we'd need to handle reltive fontsizes (ie "smaller") as well.
        bg_color = self._style.get("figure.facecolor", "white")
        opts = {
            "fontsize": self._nwc_style["annotation.fontsize"],
            "textcoords": "offset pixels",
            "path_effects": outline(bg_color),
        }
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
            msg = f"'{direction}' is an unknown direction for an annotation"
            raise Exception(msg)

        # Override default opts if passed to the function
        opts.update(kwargs)

        ann = self.ax.annotate(text, xy=xy, **opts)
        # ann = self.ax.text(text, xy[0], xy[1])
        self._annotations.append(ann)

        return ann

    def _add_caption(self, caption, hextent=None):
        """Add a caption. Supports multiline input.

        Hextent is the left/right extent,  e.g. to avoid overlapping a logo
        """
        # Wrap=true is hardcoded to use the extent of the whole figure
        # Our workaround is to resize the figure, draw the text to find the
        # linebreaks, and then restore the original width!
        if hextent is None:
            hextent = (0, self._w)
        self._set_size(hextent[1] - hextent[0])
        x1 = hextent[0] / self._w
        text = self._fig.text(
            x1,
            0.01,
            caption,
            in_layout=True,
            color=self._nwc_style["neutral_color"],
            wrap=True,
            fontsize=self._nwc_style["caption.fontsize"],
        )
        self._fig.canvas.draw()
        wrapped_text = text._get_wrapped_text()
        text.set_text(wrapped_text)
        self._set_size(self._w)

        self._caption_elem = text

    def _add_title(self, title_text):
        """Add a title."""
        text = self._fig.suptitle(
            title_text, wrap=True,
            x=0,
            y=0.985,  # default: 0.98
            horizontalalignment="left",
            multialignment="left",
            fontproperties=self._title_font,
        )

        self._title_elem = text

    def _add_subtitle(self, subtitle_text):
        y_pos = 1 - self._title_rel_height
        text = self._fig.text(
            0,
            y_pos,
            subtitle_text,
            wrap=True,
            verticalalignment="top",
            linespacing=1.4,
            fontsize=self._nwc_style["subtitle.fontsize"],
        )
        self._fig.canvas.draw()
        wrapped_text = text._get_wrapped_text()
        text.set_text(wrapped_text)
        self._set_size(self._w)
        self._subtitle_elem = text

    def _add_note(self, note_text):
        y_pos = self._footer_rel_height
        text = self._fig.text(0, y_pos, note_text, wrap=True,
                              fontsize=self._nwc_style["note.fontsize"])
        self._fig.canvas.draw()
        wrapped_text = text._get_wrapped_text()
        text.set_text(wrapped_text)
        self._set_size(self._w)
        self._note_elem = text

    def _add_xlabel(self, label):
        """Adds a label to the x axis."""
        self.ax.set_xlabel(label)

    def _add_ylabel(self, label):
        """Adds a label to the y axis."""
        self.ax.set_ylabel(label)

    def _add_data(self):
        """ Plot data to the chart.
        Typically defined by a more specific subclass
        """
        pass
        # raise NotImplementedError("This method should be overridden")

    def _mark_broken_axis(self, axis="y"):
        """Adds a symbol to mark that an axis is broken
        """
        if axis != "y":
            raise NotImplementedError("Not able to mark broken x axis yet")
        # create a custom marker path
        # Set the relative size of each move
        x_step = 0.5
        y_step = 0.3
        verts = [
            (0, 0),
            (0, y_step),
            (-x_step, y_step * 1.5),
            (x_step, y_step * 2.5),
            (-x_step, y_step * 3.5),
            (x_step, y_step * 4.5),
            (0, y_step * 5),
            (0, y_step * 6),
        ]
        codes = [Path.MOVETO] + (len(verts) - 1) * [Path.LINETO]
        path = Path(verts, codes)

        kwargs = dict(
            marker=path,
            # TODO: Make size a function of the size of the chart
            markersize=25,
            linestyle='none',
            mec=self._style["ytick.color"],
            mew=0.75,
            color='none',
            clip_on=False
        )
        self.ax.plot([0], transform=self.ax.transAxes, **kwargs)

    def _set_date_ticks(self, dates):
        """ Set x ticks and formatters for chart types working on date series """

        # Number of days on x axis (Matplotlib will use days as unit here)
        xmin, xmax = to_date(self.data.x_points[0]), to_date(self.data.x_points[-1])
        delta = xmax - xmin

        # X ticks
        if self.ticks:
            self.ax.set_xticks([x[0] for x in self.ticks])
            self.ax.set_xticklabels([x[1] for x in self.ticks])

        elif delta.days > 500:
            ticks = get_year_ticks(xmin, xmax, max_ticks=self.max_ticks)
            self.ax.set_xticks(ticks)
            self.ax.xaxis.set_major_formatter(DateFormatter('%Y'))

        else:
            loc = get_best_locator(delta, len(dates), self.interval)
            self.ax.xaxis.set_major_locator(loc)
            formatter = Formatter(self._language)

            # if isinstance(loc, WeekdayLocator):
            if self.interval == "weekly":
                # We consider dates to be more informative than week numbers
                def fmt(x, pos):
                    if pos > len(self.data.x_points):
                        return None
                    try:
                        return formatter.date(self.data.x_points[pos], "d MMM")
                    except IndexError:
                        return None
                # fmt = DateFormatter('%-d %b')
            # elif isinstance(loc, MonthLocator):
            elif self.interval in ["monthly", "quarterly"]:
                def fmt(x, pos):
                    d = num2date(x).isoformat()[:10]
                    if d not in self.data.x_points:
                        return None
                    if pos > len(self.data.x_points):
                        return None
                    if len(self.data.x_points) > 12 and d[5:7] == "01":
                        return formatter.date(d, "MMM\ny")
                    else:
                        return formatter.date(d, "MMM")
                # fmt = DateFormatter('%b')

            # elif isinstance(loc, DayLocator):
            elif self.interval == "daily":
                def fmt(x, pos):
                    d = num2date(x).isoformat()[:10]
                    if pos > len(self.data.x_points):
                        return None
                    try:
                        if len(self.data.x_points) > 7:
                            return formatter.date(d, "d MMM")
                        elif pos == 0:
                            return formatter.date(d, "EE d/M")
                        else:
                            return formatter.date(d, "EEE")
                    except IndexError:
                        return None
            else:
                NotImplementedError("Unable to determine tick formatter")

            self.ax.xaxis.set_major_formatter(fmt)

    def _apply_changes_before_rendering(self, factor=1, transparent=False):
        """
         To ensure consistent rendering, we call this method just before
         rendering file(s). This is where all properties are applied.
        """
        # Apply all changes, in the correct order for consistent rendering
        if len(self.data):
            self._add_data()

        # Calculate size in inches
        # Until 1.45 we did this on init, but now we'd like to enable dynamic heights
        if self.requested_height is None:
            h = self._get_height(int(self.requested_width))
        else:
            h = int(self.requested_height)
        self._h = h  # This was tentatively set in init. Overwritten here!
        self._set_size(self._w, h)

        # Legend / data labels
        if self.legend_title:
            # Legend can contain data labels (.labels[]),
            # or custom legends set by specific charts,
            # e.g. choropleth map colors or bar chart colors
            self.ax.get_legend().set_title(self.legend_title)

        if not self.show_ticks:
            self.category_axis.set_visible(False)
        else:
            # Increase number of decimals until we have no duplicated y axis ticks,
            # unless .decimals explicitly set.
            self._fig.canvas.draw()
            tl = [x.get_text() for x in self.value_axis.get_ticklabels()]
            tl_ = [x for (i, x) in enumerate(tl) if tl[i - 1] != x]
            autodetect_decimals = self.decimals is None
            if len(tl_) < len(tl) and autodetect_decimals:
                try_dec = 1
                keep_trying = True
                while keep_trying:
                    self.decimals = try_dec
                    if len(self.data):
                        self._add_data()
                    self._fig.canvas.draw()
                    tl = [x.get_text() for x in self.value_axis.get_ticklabels()]
                    tl_ = [x for (i, x) in enumerate(tl) if tl[i - 1] != x]
                    if len(tl) == len(tl_):
                        keep_trying = False
                    if try_dec > 2:
                        keep_trying = False
                    try_dec += 1
            # If we still have duplicates; remove them!
            # If we still have duplicates; remove them!
            ticks = self.value_axis.get_ticklabels()
            ticks_ = [x for (i, x) in enumerate(ticks) if ticks[i - 1].get_text() != x.get_text()]
            if len(ticks_) < len(ticks):
                y = [float(x._y) for x in ticks_]
                if self.decimals == 0:
                    # Recrate with integeres
                    import math
                    _bottom = min(y)
                    _top = math.ceil(max(y))
                    _bottom, _top = int(_bottom), int(_top)
                    y = range(_bottom, _top + 1)
                    y = [float(x) for x in y]
                self.value_axis.set_ticks(y)

        for a in self.annotations:
            self._annotate_point(a["text"], a["xy"], a["direction"])
        if self.ylabel is not None:
            self._add_ylabel(self.ylabel)
        if self.xlabel is not None:
            self._add_xlabel(self.xlabel)
        if self.title is not None:
            self._add_title(self.title)
        if self.subtitle is not None:
            self._add_subtitle(self.subtitle)

        # fit ticks etc.
        self._fig.tight_layout()

        logo = self._nwc_style.get("logo", self.logo)
        caption_hextent = None  # set this if adding a logo
        if logo:
            im = Image.open(logo)

            if not transparent:
                # Convert trnasparency to white,
                # to avoid some vektor format artifacts
                im = im.convert(mode="RGBA")
                _ = Image.new("RGBA", im.size, "WHITE")
                _.paste(im, (0, 0), im)
                _.convert("RGB")
                im = _

            # Scale up to at least 150 * factor,
            # but no more than a quarter of the width
            # if possible
            new_width = min(
                155 * factor,
                (self._w * factor) / 4,
            )
            new_width = min(
                im.size[0],
                new_width,
            )
            new_height = new_width * (im.size[1] / im.size[0])
            im.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)
            # Position
            if self._locale.text_direction == "rtl":
                logo_im = self._fig.figimage(im, 0, 0)
                ext = logo_im.get_extent()
                caption_hextent = (ext[1], self._w * factor)
            else:
                logo_im = self._fig.figimage(im, self._w * factor - new_width, 0)
                ext = logo_im.get_extent()
                caption_hextent = (0, ext[0])
            self._logo_elem = logo_im

        if self.caption is not None:
            # Add caption without image
            self._add_caption(self.caption, hextent=caption_hextent)

        if self.note is not None:
            self._add_note(self.note)

        # Fit header
        header_height = 0
        if self._title_elem:
            header_height += self._title_rel_height
        if self._subtitle_elem:
            header_height += self._subtitle_rel_height
        self._fig.subplots_adjust(top=1 - header_height)

        # Fit area below chart
        try:
            tick_label_height = max([self._text_rel_height(lbl)
                                    for lbl in self.ax.get_xticklabels()])
        except ValueError:
            # handle charts without ticks
            tick_label_height = 0

        sub_canvas_height = (
            # ticks labels
            tick_label_height
            # some padding
            + 30 / self._h
            #  chart notes (if any)
            + self._note_rel_height
            #  chart caption and logo (if any)
            + self._footer_rel_height
        )
        # print(sub_canvas_height, self._note_rel_height, self._footer_rel_height)
        self._fig.subplots_adjust(bottom=sub_canvas_height)

    @classmethod
    def init_from(cls, args: dict, storage=LocalStorage(),
                  style: str="newsworthy", language: str='en-GB'):
        """Create a chart from a Python object."""
        if not ("width" in args and "height" in args):
            raise Exception("The settings object must include an explicit width and height")
        chart = cls(args["width"], args["height"], storage=storage,
                    style=style, language=language)

        # Get everything from args that is a public attribute in Chart,
        # except data and labels.
        class_attrs = vars(chart)
        for k, v in args.items():
            if (not k.startswith("_")) and \
               (k in class_attrs) and \
               (k not in ["data", "labels", "ymin", "ymax", "title", "units"]):
                setattr(chart, k, v)
        if "data" in args:
            for data in args["data"].copy():
                chart.data.append(data)
        if "labels" in args:
            for label in args["labels"].copy():
                chart.labels.append(label)
        # Special handling for setters
        if "title" in args:
            chart.title = args["title"]
        if "units" in args:
            chart.units = args["units"]
        if "ymin" in args:
            chart.ymin = args["ymin"]
        if "ymax" in args:
            chart.ymax = args["ymax"]
        if "ticks" in args:
            chart.ticks = args["ticks"]
        return chart

    def render(
        self,
        key: str,
        img_format: str,
        transparent: bool=False,
        factor: int=1,
        storage_options: dict={}
    ):
        """Render file, and send to storage."""
        # Apply all changes, in the correct order for consistent rendering
        self._apply_changes_before_rendering(factor=factor, transparent=transparent)

        # Save plot in memory, to write it directly to storage
        buf = BytesIO()
        args = {
            'format': img_format,
            'transparent': transparent,
            'dpi': self._fig.dpi * factor,
        }
        if img_format == "pdf":
            args["metadata"] = {
                'Creator': "Newsworthy",
                'Producer': f"NWCharts {__version__}",
            }
        elif img_format == "png":
            args["metadata"] = {
                'Author': "Newsworthy",
                'Software': f"NWCharts {__version__}",
            }
        elif img_format == "svg":
            args["metadata"] = {
                'Publisher': "Newsworthy",
                'Creator': f"NWCharts {__version__}",
            }
        elif img_format in ["jpg", "jpeg"]:
            args["pil_kwargs"] = {
                "quality": 100,
                "optimize": True,
            }
            # Not currently supported https://github.com/matplotlib/matplotlib/issues/25401
            """
            args["metadata"] = {
                'Publisher': "Newsworthy",
                'Creator': f"NWCharts {__version__}",
            }
            """
        self._fig.savefig(buf, **args)
        buf.seek(0)
        self._storage.save(key, buf, img_format, storage_options)

    def render_all(self, key: str, transparent=False, factor=1, storage_options={}):
        """
        Render all available formats
        """
        # Apply all changes, in the correct order for consistent rendering
        self._apply_changes_before_rendering(factor=factor, transparent=transparent)

        for file_format in self.file_types:
            if file_format == "dw":
                continue

            # Save plot in memory, to write it directly to storage
            buf = BytesIO()
            args = {
                'format': file_format,
                'transparent': transparent,
                'dpi': self._fig.dpi * factor,
            }
            if file_format == "pdf":
                args["metadata"] = {
                    'Creator': "Newsworthy",
                    'Producer': f"NWCharts {__version__}",
                }
            elif file_format == "png":
                args["metadata"] = {
                    'Author': "Newsworthy",
                    'Software': f"NWCharts {__version__}",
                }
            elif file_format == "svg":
                args["metadata"] = {
                    'Publisher': "Newsworthy",
                    'Creator': f"NWCharts {__version__}",
                }
            elif file_format in ["jpg", "jpeg"]:
                args["pil_kwargs"] = {
                    "quality": 100,
                    "optimize": True,
                }
                """
                Not yet implemented in Pillow
                args["metadata"] = {
                    'Publisher': "Newsworthy",
                    'Creator': f"NWCharts {__version__}",
                }
                """
            self._fig.savefig(buf, **args)
            buf.seek(0)
            self._storage.save(key, buf, file_format, storage_options)

    @property
    def title(self):
        """ A user could have manipulated the fig property directly,
        so check for a title there as well.
        """
        if self._title is not None:
            return self._title
        elif self._fig._suptitle:
            return self._fig._suptitle.get_text()
        else:
            return None

    @title.setter
    def title(self, title: str):
        self._title = title

    @property
    def units(self):
        return self._units

    @units.setter
    def units(self, val: str):
        """ Units, used for number formatting. Note that 'degrees' is designed
        for temperature degrees.
        In some languages there are typographical differences between
        angles and short temperature notation (e.g. 45° vs 45 °).
        """
        if val == "count":
            val = "number"
            warnings.warn(
                "'count' is deprecated. "
                + "Use 'number', and manually set decimals=0 to get the same behaviour"
            )
        allowed_units = ["number", "percent", "degrees"]
        if val in allowed_units:
            self._units = val
        else:
            raise ValueError("Supported units are: {}".format(allowed_units))

    @property
    def _title_rel_height(self):
        rel_height = 0
        if self._title_elem:
            rel_height += self._text_rel_height(self._title_elem)
            # Adds a fixed margin below
            rel_height += 30 / self._h
        return rel_height

    @property
    def _subtitle_rel_height(self):
        rel_height = 0
        if self._subtitle_elem:
            rel_height += self._text_rel_height(self._subtitle_elem)
            # Adds a fixed margin below
            rel_height += 15 / self._h
        return rel_height

    @property
    def _note_rel_height(self):
        rel_height = 0
        if self._note_elem:
            rel_height += self._text_rel_height(self._note_elem)
            # Adds a fixed margin below
            rel_height += 10 / self._h
        return rel_height

    @property
    def _footer_rel_height(self):
        footer_elem_heights = [0]
        if self._logo_elem:
            # Assuming the logo is place at fixed bottom
            logo_height = self._logo_elem.get_extent()[3]
            footer_elem_heights.append(logo_height / self._h)

        if self._caption_elem:
            # Increase the bottom padding by the height of the text bbox
            caption_height = self._text_rel_height(self._caption_elem)
            footer_elem_heights.append(caption_height)

        footer_height = max(footer_elem_heights)
        footer_height += 15 / self._h

        return footer_height

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
                                                    w=self._w, h=self._h)
