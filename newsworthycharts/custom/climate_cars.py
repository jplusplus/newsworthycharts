"""Custom charts for climate report on cars
"""

from math import atan2, degrees
import numpy as np
from newsworthycharts import SerialChart
from datetime import datetime


class ClimateCarsYearlyEmissionsTo2030(SerialChart):
    # 2030 emission level target
    def __init__(self, *args, **kwargs):
        self.target = None
        self.target_label = None
        super().__init__(*args, **kwargs)

    def _add_data(self):
        super(ClimateCarsYearlyEmissionsTo2030, self)._add_data()
        color_observed = self._nwc_style["neutral_color"]
        color_scen = self._nwc_style["strong_color"]
        color_target = self._nwc_style["qualitative_colors"][1]

        self.ax.set_ylabel("Miljoner ton", style="italic")
        ###
        # Lines
        ###
        line_observed = self.ax.get_lines()[0]
        line_observed.set_color(color_observed)

        line_scen1 = self.ax.get_lines()[1]
        line_scen1.set_linestyle("dashed")
        line_scen1.set_color(color_scen)

        line_scen2 = self.ax.get_lines()[2]
        line_scen2.set_linestyle("dashed")
        line_scen2.set_color(color_scen)
        line_scen2.set_label(None)

        ###
        # Annotations
        ###
        # Target
        import matplotlib.patheffects as pe
        bg_color = self._style.get("figure.facecolor", "white")
        white_outline = [pe.withStroke(linewidth=3, foreground=bg_color)]

        self.ax.axhline(self.target, lw=1.5,
                        color=color_target)

        xmid = line_observed.get_xdata()[int(len(line_observed.get_xdata()) / 2)]
        self.ax.annotate(
            self.target_label,
            xy=(xmid, self.target),
            xytext=(-40, -30), textcoords='offset pixels',
            ha="right", va="center",
            fontweight="normal",
            fontsize=self._nwc_style["annotation.fontsize"],
            color=self._nwc_style["dark_gray_color"],
            path_effects=white_outline,
            arrowprops=dict(
                color=self._nwc_style["dark_gray_color"],
                arrowstyle="->",
                connectionstyle="angle3,angleA=-10,angleB=60",
            ),
        )

        # Scenario 1
        i_2030 = line_scen1.get_xdata().tolist().index(datetime(2030, 1, 1))

        self.ax.annotate(
            self.labels[1],
            color=self._nwc_style["dark_gray_color"],
            va="center", ha="left",
            path_effects=white_outline,
            fontsize=self._nwc_style["annotation.fontsize"],
            xytext=(40, 80), textcoords='offset pixels',
            xy=(line_scen1.get_xdata()[i_2030], line_scen1.get_ydata()[i_2030]),
            arrowprops=dict(
                color=self._nwc_style["dark_gray_color"],
                arrowstyle="->",
                connectionstyle="angle3,angleA=0,angleB=60",
            )
        )

        # Scenario 2
        self.ax.annotate(self.labels[2],
                         color=self._nwc_style["dark_gray_color"],
                         path_effects=white_outline,
                         va="center", ha="right",
                         xytext=(-40, -40), textcoords='offset pixels',
                         xy=(line_scen2.get_xdata()[i_2030],
                             line_scen2.get_ydata()[i_2030]),
                         fontsize=self._nwc_style["annotation.fontsize"],
                         arrowprops=dict(
                             color=self._nwc_style["dark_gray_color"],
                             arrowstyle="->",
                             connectionstyle="angle3,angleA=-10,angleB=60")
                         )

        ###
        # Legend
        ###

        # colors = [color_observed, color_scen]
        lines = self.ax.get_lines()[:2]
        labels = ['Historiska utsläpp', 'Utsläppsscenarier']
        self.ax.legend(lines, labels)
        tick_years = [line_observed.get_xdata()[0].year, 2010, 2020, 2030, 2045]
        self.ax.set_xticks([datetime(x, 1, 1) for x in tick_years])


class ClimateCarsCO2BugdetChart(SerialChart):
    pass

    def __init__(self, *args, **kwargs):
        self.budget = None
        self.budget_label = None
        self.line_annotations = []
        super().__init__(*args, **kwargs)

    def _add_data(self):
        super(ClimateCarsCO2BugdetChart, self)._add_data()
        # color_observed = self._nwc_style["neutral_color"]
        color_scen = self._nwc_style["strong_color"]
        color_budget = self._nwc_style["qualitative_colors"][1]

        self.ax.set_ylabel("Miljoner ton", style="italic")
        ###
        # Lines
        ###
        # line_observed = self.ax.get_lines()[0]
        # line_observed.set_color(color_observed)

        line_scen1 = self.ax.get_lines()[0]
        line_scen1.set_linestyle("dashed")
        line_scen1.set_color(color_scen)

        line_scen2 = self.ax.get_lines()[1]
        line_scen2.set_linestyle("dashed")
        line_scen2.set_color(color_scen)
        line_scen2.set_label(None)

        ###
        # Annotations
        ###
        import matplotlib.patheffects as pe

        def outline(color):
            return [pe.withStroke(linewidth=3, foreground=color)]

        xmin = line_scen1.get_xdata()[0]
        xmax = line_scen1.get_xdata()[-1]
        s1_ymax = line_scen1.get_ydata()[-1]
        s2_ymax = line_scen2.get_ydata()[-1]

        self.ax.set_ylim(0, s1_ymax * 1.2)

        # budgettak
        self.ax.axhline(self.budget, lw=1.5, color=color_budget)
        self.ax.axhspan(self.budget, self.ax.get_ylim()[1], facecolor=color_budget,
                        edgecolor=None, alpha=.3)

        self.ax.annotate(
            self.budget_label,
            xy=(xmin, self.budget),
            xytext=(0, 5), textcoords="offset pixels",
            ha="left", va="bottom",
            fontweight="bold",
            fontsize=self._nwc_style["annotation.fontsize"],
            color=color_budget,
            # path_effects=white_outline,
        )

        # scen 1: nuvarande utsläpp
        a = self.line_annotations[0]
        self.ax.annotate(
            a[2],
            color=self._nwc_style["dark_gray_color"],
            va="center", ha="right",
            # path_effects=outline(color_budget),
            fontsize=self._nwc_style["annotation.fontsize"],
            xytext=(-40, 120), textcoords='offset pixels',
            xy=(datetime.strptime(a[0], "%Y-%m-%d"), a[1]),
            arrowprops=dict(
                color=self._nwc_style["dark_gray_color"],
                arrowstyle="->",
                connectionstyle="angle3,angleA=0,angleB=-60",
            ),
        )

        self.ax.annotate(
            self.labels[0],
            xy=(xmax, s1_ymax),
            xytext=(-30, 0), textcoords='offset pixels',
            color=color_scen,
            va="bottom", ha="right",
            fontsize=self._nwc_style["annotation.fontsize"],
        )

        # scen 2: nuvarande utsläpp
        a = self.line_annotations[1]
        self.ax.annotate(
            a[2],
            color=self._nwc_style["dark_gray_color"],
            va="center", ha="left",
            xytext=(20, -80), textcoords='offset pixels',
            xy=(datetime.strptime(a[0], "%Y-%m-%d"), a[1]),
            fontsize=self._nwc_style["annotation.fontsize"],
            arrowprops=dict(
                color=self._nwc_style["dark_gray_color"],
                arrowstyle="->",
                connectionstyle="angle3,angleA=0,angleB=-60"
            )
        )

        self.ax.annotate(
            self.labels[1],
            xy=(xmax, s2_ymax),
            xytext=(-30, 0), textcoords='offset pixels',
            color=color_scen,
            va="bottom", ha="right",
            fontsize=self._nwc_style["annotation.fontsize"],
        )

        self.ax.get_legend().remove()


# Label line with line2D label data
def label_line(line, x, label=None, align=True, **kwargs):

    ax = line.axes
    xdata = line.get_xdata()
    ydata = line.get_ydata()

    if (x < xdata[0]) or (x > xdata[-1]):
        print('x label location is outside data range!')
        return

    # Find corresponding y co-ordinate and angle of the line
    ip = 1
    for i in range(len(xdata)):
        if x < xdata[i]:
            ip = i
            break

    y = ydata[ip - 1] + (ydata[ip] - ydata[ip - 1]) * (x - xdata[ip - 1]) / (xdata[ip] - xdata[ip - 1])

    if not label:
        label = line.get_label()

    if align:
        # Compute the slope
        dx = (xdata[ip] - xdata[ip - 1])
        dy = ydata[ip] - ydata[ip - 1]
        ang = degrees(atan2(dy, dx))

        # Transform to screen co-ordinates
        pt = np.array([x, y]).reshape((1, 2))
        ang = 45
        trans_angle = ax.transData.transform_angles(np.array((ang,)), pt)[0]

    else:
        trans_angle = 0

    # Set a bunch of keyword arguments
    if 'color' not in kwargs:
        kwargs['color'] = line.get_color()

    if ('horizontalalignment' not in kwargs) and ('ha' not in kwargs):
        kwargs['ha'] = 'center'

    if ('verticalalignment' not in kwargs) and ('va' not in kwargs):
        kwargs['va'] = 'center'

    if 'backgroundcolor' not in kwargs:
        kwargs['backgroundcolor'] = ax.get_facecolor()

    if 'clip_on' not in kwargs:
        kwargs['clip_on'] = True

    if 'zorder' not in kwargs:
        kwargs['zorder'] = 2.5

    ax.text(x, y, label, rotation=trans_angle, **kwargs)
