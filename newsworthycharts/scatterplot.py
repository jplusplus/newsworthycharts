from .chart import Chart

from adjustText import adjust_text


class ScatterPlot(Chart):
    """ Make two-dimensional scatterplots
    """

    def __init__(self, *args, **kwargs):
        super(ScatterPlot, self).__init__(*args, **kwargs)

    def _add_data(self):
        # Use value formatter for both axis
        va_formatter = self._get_value_axis_formatter()
        self.ax.xaxis.set_major_formatter(va_formatter)
        self.ax.yaxis.set_major_formatter(va_formatter)
        self.ax.grid(True)

        for data in self.data:
            x = [float(d[0]) for d in data]
            y = [float(d[1]) for d in data]
            try:
                value_labels = [d[2] for d in data]
            except IndexError:
                value_labels = [None] * len(data)

            # Make markers semi-transparent
            transparent_color = list(self._style["neutral_color"])
            transparent_color[3] = .3
            colors = [transparent_color] * len(data)
            # s refers to area here, so square the marker size
            markersize = self._style["lines.markersize"]**2
            self.ax.scatter(x, y, c=colors, zorder=1, marker='o', s=markersize)

            # Value labels and highlights are added as an additional layer above
            # base chart
            for i, value_label in enumerate(value_labels):
                if value_label is not None:
                    # A point can be both highlighted and annotated
                    if (self.highlight is not None) and \
                            (value_label == self.highlight or value_label in self.highlight):
                        color = self._style["strong_color"]
                        size = self._style["lines.markersize"] * 1.5
                        fontsize = "medium"
                    # ...or just annotated
                    else:
                        color = transparent_color
                        size = self._style["lines.markersize"]
                        fontsize = "small"

                    # the dot
                    self.ax.plot(x[i], y[i],
                                 color=color,
                                 zorder=5,
                                 marker='o',
                                 markersize=size)
                    # the text
                    self._annotate_point(value_label,
                                         (x[i], y[i]),
                                         "up",
                                         fontsize=fontsize,
                                         zorder=5)

            adjust_text(self._annotations, autoalign="y",
                        expand_points=(1.5, 1.5),
                        rrowprops=dict(arrowstyle=" - ", lw=1))
