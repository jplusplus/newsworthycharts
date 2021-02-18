from .chart import Chart
from .lib.utils import to_float

import numpy as np


class CategoricalChart(Chart):
    """ Plot categorical data to a bar chart, e.g. number of llamas per country
    """

    def __init__(self, *args, **kwargs):
        super(CategoricalChart, self).__init__(*args, **kwargs)
        self.bar_orientation = "horizontal"  # [horizontal|vertical]
        self.annotation_rotation = 0
        self.stacked = False

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

        if self.stacked:
            bar_width = 0.8
        else:
            bar_width = 0.8 / len(self.data)
        self.bar_width = bar_width

        # parse values
        serie_values = []
        for serie in self.data:
            _values = [to_float(x[1]) for x in serie]
            # Replace None values with 0's to be able to plot bars
            _values = [0 if v is None else v for v in _values]
            serie_values.append(_values)

        cum_values = np.cumsum(serie_values, axis=0).tolist()

        for i, data in enumerate(self.data):

            # Replace None values with 0's to be able to plot bars
            values = serie_values[i]
            categories = [x[0] for x in data]
            try:
                serie_label = self.labels[i]
            except IndexError:
                serie_label = None

            color = self._style["neutral_color"]
            highlight_color = self._style["strong_color"]

            if self.highlight is None:
                # use strong color if there is nothing to highlight
                colors = [highlight_color] * len(values)
            elif self.stacked and serie_label == self.highlight:
                # hihglight by serie label when bars are stacked
                colors = [highlight_color] * len(values)
            else:
                # TODO: More coloring options for stacked bars
                colors = [color] * len(values)

            # Add any annotations given inside the data
            # and also annotate highlighted value
            for j, d in enumerate(data):
                if d[1] is None:
                    # Dont annotate None values
                    continue
                # Get position for any highlighting to happen
                if self.bar_orientation == "horizontal":
                    xy = (d[1], j)
                    if d[1] >= 0:
                        dir = "right"
                    else:
                        dir = "left"
                else:
                    xy = (j, d[1])
                    if d[1] >= 0:
                        dir = "up"
                    else:
                        dir = "down"

                if d[2] is not None:
                    self._annotate_point(d[2], xy, direction=dir, rotation=self.annotation_rotation)
                elif self.highlight is not None and self.highlight == d[0]:
                    # Only add highlight value if not already annotated
                    self._annotate_point(a_formatter(d[1]), xy, direction=dir, rotation=self.annotation_rotation)

                if self.highlight is not None and self.highlight == d[0]:
                    colors[j] = highlight_color

            if self.stacked:
                bar_pos = np.arange(len(values))
            else:
                bar_pos = [x + i * bar_width
                             for x in np.arange(len(values))]


            if self.bar_orientation == "horizontal":
                kwargs = dict(align='center', height=bar_width,
                              color=colors, zorder=2)
                if self.stacked and i > 0:
                    # To make stacked bars we need to set bottom value
                    kwargs["left"] = cum_values[i-1]

                self.ax.barh(bar_pos, values, **kwargs)

            elif self.bar_orientation == "vertical":
                kwargs = dict(width=bar_width, color=colors,
                            zorder=2)
                if self.stacked and i > 0:
                    # To make stacked bars we need to set bottom value
                    kwargs["bottom"] = cum_values[i-1]
                self.ax.bar(bar_pos, values, **kwargs)

        margin = 0.02 # above and below first/last bar on horizontal 
        if self.bar_orientation == "horizontal":
            self.ax.set_yticks(bar_pos)
            self.ax.set_yticklabels(categories)
            self.ax.invert_yaxis()
            self.ax.margins(0,margin)


            # Make sure labels are not cropped
            yaxis_bbox = self.ax.yaxis.get_tightbbox(self._fig.canvas.renderer)
            margin = self._style["figure.subplot.left"]
            margin -= yaxis_bbox.min[0] / float(self._w)
            self._fig.subplots_adjust(left=margin)

        elif self.bar_orientation == "vertical":
            self.ax.margins(margin,0)
            self.ax.set_xticks(bar_pos)
            self.ax.set_xticklabels(categories)
            self.ax.xaxis.set_ticks_position('none')


        if len(self.data) > 1:
            self.ax.legend(self.labels, loc='best')


class CategoricalChartWithReference(CategoricalChart):
    """ A two categorical chart with two series where the latter is treated
    as a reference line.
    """

    def _add_data(self):
        allowed_orientations = ["horizontal", "vertical"]
        if self.bar_orientation not in allowed_orientations:
            raise ValueError(f"Valid oriantations: {allowed_orientations}")

        if len(self.data) != 2:
            raise ValueError("This chart is expecting two series")

        if self.bar_orientation == "horizontal":
            self.value_axis = self.ax.xaxis
            self.category_axis = self.ax.yaxis

        a_formatter = self._get_annotation_formatter()
        va_formatter = self._get_value_axis_formatter()
        self.value_axis.set_major_formatter(va_formatter)
        self.value_axis.grid(True)

        bar_width = 0.8 / len(self.data)
        for i, data in enumerate(self.data):

            # Replace None values with 0's to be able to plot bars
            values = [0 if x[1] is None else float(x[1]) for x in data]
            categories = [x[0] for x in data]

            if i == 0:
                color = self._style["strong_color"]
            else:
                color = self._style["neutral_color"]

            bar_pos = [x + i * bar_width / 2
                         for x in np.arange(len(values))]
            tick_pos = [x - bar_width / 4 for x in bar_pos]

            zorder = len(self.data) - i
            if self.bar_orientation == "horizontal":
                self.ax.barh(bar_pos, values, height=bar_width, align='center',
                             color=color, zorder=zorder)
                self.ax.set_yticks(tick_pos)
                self.ax.set_yticklabels(categories)
                #self.ax.invert_yaxis()


            elif self.bar_orientation == "vertical":
                self.ax.bar(bar_pos, values, width=bar_width, color=color,
                            zorder=zorder)
                self.ax.set_xticks(tick_pos)
                self.ax.set_xticklabels(categories)
                self.ax.xaxis.set_ticks_position('none')


        # Make sure labels are not cropped
        yaxis_bbox = self.ax.yaxis.get_tightbbox(self._fig.canvas.renderer)
        margin = self._style["figure.subplot.left"]
        margin -= yaxis_bbox.min[0] / float(self._w)
        self._fig.subplots_adjust(left=margin)


        if self.labels:
            self.ax.legend(self.labels, loc='best')


class ProgressChart(CategoricalChart):
    def __init__(self, *args, **kwargs):
        self.target = None
        self.target_label = None

        # should value labels be rendered? 
        self.value_labels = None # "progress"|"remaining"


        super().__init__(*args, **kwargs)
        self.stacked = True

    def _add_data(self):
        if self.target is None:
            raise ValueError("A target must be defined to make a ProgressChart")
        
        if len(self.data) > 1:
            raise ValueError("ProgressChart takes one data series only.")
        
        s_progress = self.data[0]
        s_remaining = [(x[0], max(0, self.target - x[1])) for x in s_progress]
        categories = [x[0] for x in s_progress]

        self.data.append(s_remaining)

        super(ProgressChart, self)._add_data()
        n_bars = len(self.data[0])
        color_progress = self._style["strong_color"]
        color_remaining = self._style["light_gray_color"]

        # BAR STYLING
        for rect in self.ax.patches[n_bars:]:
            #rect.set_alpha(.5)
            #color = rect.get_facecolor()
            rect.set_facecolor(color_remaining)
            rect.set_alpha(.5)

            #rect.set_linewidth(1)
            #rect.set_edgecolor(color_progress)


        # LABELING: Target
        if self.target_label:
            offset = 25

            target_label_x = self.target
            target_label_y = self.ax.patches[0].xy[1]

            self.ax.annotate(self.target_label,
                        (target_label_x, target_label_y),
                        xytext=(-offset, offset), 
                        textcoords='offset pixels',
                        ha="right", va="bottom",
                        fontsize=self._style["annotation.fontsize"],
                        arrowprops={
                            "arrowstyle": "-",
                            #"shrinkA": 0, "shrinkB": dot_size / 2 + 2,
                            "connectionstyle": "angle,angleA=0,angleB=90,rad=0",
                            "color": self._style["neutral_color"],
                        })
        
        # LABELING: Value labels
        if self.value_labels:
            fmt = self._get_value_axis_formatter()
            if self.value_labels == "progress":
                val_labels = [fmt(x[1]) for x in s_progress]
                val_label_orient = ["inside" if (x[1] / self.target) > .1 else "outside" 
                                    for x in s_progress]
                val_label_xpos = [x[1] for x in s_progress]
                # TODO: Dynamic coloring based on background
                val_label_color = ["white"] * n_bars
                

            elif self.value_labels == "remaining":
                val_labels = [fmt(-x[1]) for x in s_remaining]
                # We might want to reconsider placement
                val_label_orient = ["inside"] * n_bars
                val_label_xpos = [self.target for x in s_remaining]
                val_label_color = [self._style["text.color"]] * n_bars

            else:
                raise ValueError(f"Invalid value_labels value: {self.values_labels}")
            
            for i, label in enumerate(val_labels):
                xpos = val_label_xpos[i]
                ypos = self.ax.patches[i].xy[1]  + self.bar_width / 2
                orient = val_label_orient[i]
                color = val_label_color[i]
                offset = 10
                self.ax.annotate(label, (xpos, ypos),
                                 xytext=(-offset if orient == "inside" else offset, 0),
                                 textcoords='offset pixels',
                                 va="center", 
                                 ha="right" if orient == "inside" else "left",
                                 fontsize=self._style["annotation.fontsize"],
                                 color=color,
                                 )
        
        self.ax.get_legend().remove()