from .chart import Chart
from .lib.utils import adjust_lightness
from .lib.formatter import Formatter

import numpy as np


class RangePlot(Chart):
    """ Plot categorical data with two data points, for example change over time.

    Mimics Datawrapper's dito in form and functionality
    """

    def __init__(self, *args, **kwargs):
        super(RangePlot, self).__init__(*args, **kwargs)

        # Custom colors for start and end points
        self.colors = None # ["red", "green"]

        # should value labels be rendered? 
        self.values_labels = None # "start"|"end"|"difference"|"percent_change"


    def _add_data(self):

        series = self.data

        if len(series) != 2:
            raise Exception("A dumbbell chart must be made up of two series and two series only.")
        
        # assuming both series have the same index here
        categories = [d[0] for d in series[0]]
        start_values = [d[1] for d in series[0]] 
        end_values = [d[1] for d in series[1]] 
        
        dot_size = 10
        start_dots = self.ax.scatter(start_values, categories, s=pow(dot_size,2), zorder=2)
        end_dots = self.ax.scatter(end_values, categories, s=pow(dot_size,2), zorder=3, alpha=1)

        lines = self.ax.hlines(y=categories, xmin=start_values, xmax=end_values,
                               lw=dot_size*.6, zorder=1)

        # COLORING: highlight the end point by default
        if self.colors is None:
            start_color, end_color = self._style["neutral_color"], self._style["strong_color"]
        else:
            start_color, end_color = self.colors

        start_dots.set_color(start_color)
        end_dots.set_color(end_color)
        lines.set_color(adjust_lightness(end_color, 1.65))

        # LABELS: start/end label
        if self.labels:
            offset = 25
            props = dict(xytext=(0, offset), 
                        textcoords='offset pixels',
                        va="bottom",
                        #color=self._style["dark_gray_color"],
                        arrowprops={
                            "arrowstyle": "-",
                            "shrinkA": 0, "shrinkB": dot_size / 2 + 2,
                            "connectionstyle": "angle,angleA=0,angleB=90,rad=0",
                            "color":self._style["neutral_color"],
                        })
            start_value, end_value = start_values[-1], end_values[-1]
            self.ax.annotate(self.labels[1],
                        (end_value, categories[-1]),
                         color=end_color,
                         ha="right" if start_value > end_value else "left",
                        **props)

            if start_value != end_value:
                self.ax.annotate(self.labels[0],
                        (start_value, categories[-1]),
                        color=start_color, 
                        ha="right" if start_value < end_value else "left",
                        **props)

            # end of labeling

        # VALUE LABELS
        if self.values_labels:
            fmt = self._get_value_axis_formatter()
            pct_fmt = Formatter(self._language,
                                decimals=self.decimals).percent

            if self.values_labels == "start":
                val_labels = [fmt(v) for v in start_values]
                val_label_end = "start"
            
            elif self.values_labels == "end":
                val_labels = [fmt(v) for v in end_values]
                val_label_end = "end"

            elif self.values_labels == "difference":
                val_labels = [change_fmt(v - start_values[i], fmt) 
                              for i, v in enumerate(end_values)]
                val_label_end = "end"

            elif self.values_labels == "percent_change":
                val_labels = [change_fmt(v / start_values[i] - 1, pct_fmt) 
                              for i, v in enumerate(end_values)]
                val_label_end = "end"

            else:
                raise ValueError(f"Invalid value for 'self.value_labels': {self.values_labels}")
            
            # determine x positions and color of value labels
            if val_label_end == "start":
                val_label_xpos = [(v, v > end_values[i]) for i, v in enumerate(start_values)]
                val_label_color = start_color

            elif val_label_end == "end":
                val_label_xpos = [(v, v > start_values[i]) for i, v in enumerate(end_values)]
                val_label_color = end_color

            
            for label, (xpos, is_larger), ypos in zip(val_labels, val_label_xpos, categories):
                offset = dot_size * 2
                self.ax.annotate(label, (xpos, ypos),
                                 xytext=(offset if is_larger else -offset, 0),
                                 textcoords='offset pixels',
                                 va="center", 
                                 color=val_label_color,
                                 ha="left" if is_larger else "right")

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
        self.ax.grid(True)
        self.ax.margins(0.15, 0.3) # adds vertical padding
        self.ax.tick_params(axis=u'both', which=u'both',length=0) # hide ticks
        self.ax.spines['bottom'].set_visible(False) # hide line

        if self.data.min_val < 0:
            self.ax.axvline(0, lw=1.5, zorder=0)

def change_fmt(val, fmt):
    """
    """
    if val > 0:
        return "+" + fmt(val)
    else:
        return fmt(val)
