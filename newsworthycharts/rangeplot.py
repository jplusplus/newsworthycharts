from .chart import Chart
from .lib.utils import adjust_lightness
from .lib.formatter import Formatter


class RangePlot(Chart):
    """ Plot categorical data with two data points, for example change over time.

    Mimics Datawrapper's dito in form and functionality
    """
    _uses_categorical_data = False

    def __init__(self, *args, **kwargs):
        super(RangePlot, self).__init__(*args, **kwargs)

        self.value_axis = self.ax.xaxis
        self.category_axis = self.ax.yaxis

        # Custom colors for start and end points
        self.colors = None  # ["red", "green"]

        # should value labels be rendered?
        self.value_labels = None  # "start"|"end"|"difference"|"percent_change"

    def _add_data(self):

        series = self.data

        if len(series) != 2:
            raise Exception("A dumbbell chart must be made up of two series and two series only.")

        # assuming both series have the same index here
        categories = [d[0] for d in series[0]]
        start_values = [d[1] for d in series[0]]
        end_values = [d[1] for d in series[1]]

        dot_size = 10
        start_dots = self.ax.scatter(start_values, categories, s=pow(dot_size, 2), zorder=2)
        end_dots = self.ax.scatter(end_values, categories, s=pow(dot_size, 2), zorder=3, alpha=1)

        lines = self.ax.hlines(y=categories, xmin=start_values, xmax=end_values,
                               lw=dot_size * .6, zorder=1)

        # COLORING:
        if self.colors is None:
            if self.value_labels == "both":
                # use categorical coloring by default if both ends are to labelsed
                start_color = self._nwc_style["qualitative_colors"][1]
                end_color = self._nwc_style["qualitative_colors"][0]
            else:
                # highlight the end point by default
                start_color, end_color = self._nwc_style["neutral_color"], self._nwc_style["strong_color"]
        else:
            start_color, end_color = self.colors

        start_dots.set_color(start_color)
        end_dots.set_color(end_color)
        lines.set_color(adjust_lightness(end_color, 1.4))

        # LABELS: start/end label
        if self.labels:
            offset = 25
            props = dict(
                xytext=(0, offset),
                textcoords='offset pixels',
                va="bottom",
                fontsize=self._nwc_style["annotation.fontsize"],
                fontweight="bold",
                # color=self._nwc_style["dark_gray_color"],
                arrowprops={
                    "arrowstyle": "-",
                    "shrinkA": 0, "shrinkB": dot_size / 2 + 2,
                    "connectionstyle": "angle,angleA=0,angleB=90,rad=0",
                    "color": self._nwc_style["neutral_color"],
                }
            )
            start_value, end_value = start_values[-1], end_values[-1]
            end_label = self.ax.annotate(
                self.labels[1],
                (end_value, categories[-1]),
                color=end_color,
                ha="right" if start_value > end_value else "left",
                **props,
            )
            if start_value != end_value:
                self.ax.annotate(
                    self.labels[0],
                    (start_value, categories[-1]),
                    color=start_color,
                    ha="right" if start_value < end_value else "left",
                    **props
                )
            # end of labeling

        # VALUE LABELS
        val_label_elems = []
        if self.value_labels:
            fmt = self._get_value_axis_formatter()
            pct_fmt = Formatter(self._language,
                                decimals=self.decimals).percent
            n_bars = len(start_values)

            if self.value_labels == "start":
                val_labels = [fmt(v) for v in start_values]
                val_label_end = "start"

            elif self.value_labels == "end":
                val_labels = [fmt(v) for v in end_values]
                val_label_end = "end"

            elif self.value_labels == "both":
                val_labels = ([fmt(v) for v in start_values]
                              + [fmt(v) for v in end_values])
                val_label_end = "both"

            elif self.value_labels == "difference":
                val_labels = [change_fmt(v - start_values[i], fmt)
                              for i, v in enumerate(end_values)]
                val_label_end = "end"

            elif self.value_labels == "percent_change":
                val_labels = [change_fmt(v / start_values[i] - 1, pct_fmt)
                              for i, v in enumerate(end_values)]
                val_label_end = "end"

            else:
                raise ValueError(f"Invalid value for 'self.value_labels': {self.value_labels}")

            # determine x positions and color of value labels
            if val_label_end == "start":
                val_label_xpos = [(v, v > end_values[i]) for i, v in enumerate(start_values)]
                val_label_colors = [start_color] * n_bars

            elif val_label_end == "end":
                val_label_xpos = [(v, v > start_values[i]) for i, v in enumerate(end_values)]
                val_label_colors = [end_color] * n_bars

            elif val_label_end == "both":
                val_label_xpos = ([(v, v > end_values[i]) for i, v in enumerate(start_values)]
                                  + [(v, v > start_values[i]) for i, v in enumerate(end_values)])
                val_label_colors = [start_color] * n_bars + [end_color] * n_bars
                categories = categories + categories

            for label, (xpos, is_larger), val_label_color, ypos\
                    in zip(val_labels, val_label_xpos, val_label_colors, categories):
                offset = dot_size * 2
                val_label_elem = self.ax.annotate(
                    label,
                    (xpos, ypos),
                    xytext=(offset if is_larger else -offset, 0),
                    textcoords='offset pixels',
                    va="center",
                    fontsize=self._nwc_style["annotation.fontsize"],
                    color=val_label_color,
                    ha="left" if is_larger else "right",
                )
                val_label_elems.append(val_label_elem)

        if self.highlight:
            if not isinstance(self.highlight, list):
                self.highlight = [self.highlight]

            for cat_to_highlight in self.highlight:
                try:
                    i = categories.index(cat_to_highlight)
                except ValueError:
                    raise ValueError(f"Invalid higlight: {cat_to_highlight}. Try one of {categories}")

            tick_label = self.ax.yaxis.get_ticklabels()[i]
            tick_label.set_fontweight("bold")

        # Setup axes and grids
        va_formatter = self._get_value_axis_formatter()
        self.value_axis.set_major_formatter(va_formatter)
        self.ax.grid(True)

        # Setup chart area margins
        # Hack: the horizontal margins are now hard-coded to – typically – fit
        # percent values if value labels are render.
        # A proper solution would be to adjust the margin by the actual text width(s),
        # which is probably not impossible, but also not very simple.
        # The vertical padding (y_margin) is, on the other hand, dynamic.
        x_margin = 0.15 if self.value_labels else 0.05
        y_margin = 0

        if self.labels:
            # adds vertical padding
            label_height = self._text_rel_height(end_label)
            y_margin = label_height * 2

            # hack: labels end up outside canvas when there is no title/subtitle
            # by adding an empty subtitle some extra padding will be
            # added later on
            if self.title is None and self.subtitle is None:
                self.subtitle = ""

        self.ax.margins(x_margin, y_margin)

        self.ax.tick_params(axis=u'both', which=u'both', length=0)  # hide ticks
        self.ax.spines['bottom'].set_visible(False)  # hide line

        if self.data.min_val < 0:
            self.ax.axvline(0, lw=1.5, zorder=0)


def change_fmt(val, fmt):
    """
    """
    if val > 0:
        return "+" + fmt(val)
    else:
        return fmt(val)
