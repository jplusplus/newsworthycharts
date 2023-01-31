from .chart import Chart

from adjustText import adjust_text
from matplotlib.ticker import MaxNLocator


class ScatterPlot(Chart):
    """ Make two-dimensional scatterplots

    Expected data format:

    [
        [
            [X, Y, NAME],
            [X, Y, NAME],
        ],
    ]

    NAME is optional. Points are labeled based on NAME, if listed under `self.labels`
    """
    _uses_categorical_data = False

    def __init__(self, *args, **kwargs):
        super(ScatterPlot, self).__init__(*args, **kwargs)

        self.units_x = "number"
        self.units_y = "number"
        # list items to label
        self.labels = []

        self.ymin = None
        self.xmin = None

    def _add_data(self):
        # Set up axes
        x_formatter = self._get_formatter(self.units_x)
        y_fomatter = self._get_formatter(self.units_y)
        self.ax.xaxis.set_major_formatter(x_formatter)
        self.ax.yaxis.set_major_formatter(y_fomatter)
        self.ax.grid(True)

        # always show left and bottom spines
        self.ax.spines["left"].set_visible(True)
        self.ax.spines["bottom"].set_visible(True)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["top"].set_visible(False)

        # hard coded max number of ticks for now
        # consider dynamic/more clever approach
        max_ticks = 5
        self.ax.yaxis.set_major_locator(MaxNLocator(nbins=max_ticks))
        self.ax.xaxis.set_major_locator(MaxNLocator(nbins=max_ticks))

        for data in self.data:
            x = [float(d[0]) for d in data]
            y = [float(d[1]) for d in data]
            try:
                point_names = [d[2] for d in data]
            except IndexError:
                point_names = [None] * len(data)

            # Make markers semi-transparent
            transparent_color = list(self._nwc_style["neutral_color"])
            transparent_color[3] = .4

            # s refers to area here, so square the marker size
            markersize = self._style["lines.markersize"]**2

            # Value labels and highlights are added as an additional layer above
            # base chart
            label_elems = []
            for i, point_label in enumerate(point_names):
                if point_label is not None:
                    is_labeled = point_label in self.labels
                    is_highlighted = (self.highlight is not None) and \
                        (point_label == self.highlight or point_label in self.highlight)
                    markersize = 3

                    # A point can be both highlighted and annotated
                    if is_highlighted:
                        color = self._nwc_style["strong_color"]
                        size = markersize * 1.7
                        fontsize = "medium"
                    elif is_labeled:
                        color = self._nwc_style["strong_color"]
                        size = markersize
                        fontsize = "small"
                    # ...or just annotated
                    else:
                        color = transparent_color
                        size = markersize
                        fontsize = "small"

                    # the dot
                    self.ax.plot(
                        x[i], y[i],
                        color=color,
                        markeredgecolor=color,
                        zorder=5,
                        marker='o',
                        markersize=size,
                    )

                    # the text
                    if is_highlighted or is_labeled:
                        label = self._annotate_point(
                            point_label,
                            (x[i], y[i]),
                            "up",
                            fontsize=fontsize,
                            zorder=5,
                        )
                        label_elems.append(label)

            # These settings could be fine-tuned
            # Weren't able to add lines between points and labels for example
            adjust_text(self._annotations, ax=self.ax, autoalign="y",
                        expand_points=(1, 1),)

        if self.ymin is not None:
            self.ax.set_ylim(self.ymin)

        if self.xmin is not None:
            self.ax.set_xlim(self.xmin)

    # scatterplot has custom axis labels
    @property
    def _axis_label_props(self):
        """Common props for axis labels
        """
        return dict(textcoords="offset pixels", xycoords="axes fraction",
                    fontsize="small", style="italic",
                    transform=self.ax.transAxes)

    def _add_xlabel(self, label):
        self.ax.annotate(label, (1, 0), ha="right", va="bottom", xytext=(0, 5),
                         **self._axis_label_props)

    def _add_ylabel(self, label):
        self.ax.annotate(label, (0, 1), ha="left", va="top", xytext=(5, 0),
                         **self._axis_label_props)
