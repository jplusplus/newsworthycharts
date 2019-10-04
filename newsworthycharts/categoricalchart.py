from .chart import Chart

import numpy


class CategoricalChart(Chart):
    """ Plot categorical data to a bar chart, e.g. number of llamas per country
    """

    def __init__(self, *args, **kwargs):
        super(CategoricalChart, self).__init__(*args, **kwargs)
        self.bar_orientation = "horizontal"  # [horizontal|vertical]


    def _add_data(self):
        allowed_orientations = ["horizontal", "vertical"]
        if self.bar_orientation not in allowed_orientations:
            raise ValueError(f"Valid oriantations: {allowed_orientations}")

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

            color = self._style["neutral_color"]
            highlight_color = self._style["strong_color"]

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

            label_pos = numpy.arange(len(values))
            if self.bar_orientation == "horizontal":
                self.ax.barh(label_pos, values, align='center',
                             color=colors, zorder=2)
                self.ax.set_yticks(label_pos)
                self.ax.set_yticklabels(categories, fontsize='small')
                self.ax.invert_yaxis()

                # Make sure labels are not cropped
                yaxis_bbox = self.ax.yaxis.get_tightbbox(self._fig.canvas.renderer)
                margin = self._style["figure.subplot.left"]
                margin -= yaxis_bbox.min[0] / float(self._w)
                self._fig.subplots_adjust(left=margin)
            else:
                self.ax.bar(label_pos, values, color=colors, zorder=2)
                self.ax.set_xticks(label_pos)
                self.ax.set_xticklabels(categories, fontsize='small')
                self.ax.xaxis.set_ticks_position('none')
