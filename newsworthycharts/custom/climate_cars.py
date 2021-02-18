"""Custom charts for climate report on cars
"""

from newsworthycharts import SerialChart
import numpy as np

class ClimateCarsYearlyEmissionsTo2030(SerialChart):
    # 2030 emission level target
    def __init__(self, *args, **kwargs):
        self.target = None
        self.target_label = None
        super().__init__(*args, **kwargs)

    def _add_data(self):
        super(ClimateCarsYearlyEmissionsTo2030, self)._add_data()
        color_observed = self._style["neutral_color"]
        color_scen = self._style["strong_color"]
        color_target = self._style["qualitative_colors"][1]

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
        white_outline = [pe.withStroke(linewidth=3, foreground="white")]

        self.ax.axhline(self.target, lw=1.5, 
                        #ls="dashed",
                        color=color_target)
        
        xmid = line_observed.get_xdata()[int(len(line_observed.get_xdata())/2)]
        self.ax.annotate(self.target_label, 
                         xy=(xmid, self.target),
                         xytext=(-40,-30), textcoords='offset pixels',
                         ha="right", va="center",
                         fontweight="normal",
                         fontsize=self._style["annotation.fontsize"],
                         color=self._style["dark_gray_color"],
                         path_effects=white_outline,
                         arrowprops=dict(
                             color=self._style["dark_gray_color"],
                             arrowstyle="->",
                            connectionstyle="angle3,angleA=-10,angleB=60"),
            )

        # Scenario 1
        self.ax.annotate(self.labels[1], 
                         color=self._style["dark_gray_color"], 
                         va="center", ha="right",
                         path_effects=white_outline,
                         fontsize=self._style["annotation.fontsize"],
                         xytext=(-40, 120), textcoords='offset pixels',
                         xy=(line_scen1.get_xdata()[-1], 
                             line_scen1.get_ydata()[-1]),
                        arrowprops=dict(
                             color=self._style["dark_gray_color"],
                             arrowstyle="->",
                            connectionstyle="angle3,angleA=0,angleB=-60")
                             )

        # Scenario 2
        self.ax.annotate(self.labels[2], 
                         color=self._style["dark_gray_color"], 
                         path_effects=white_outline,
                         va="center", ha="right",
                         xytext=(-40, -40), textcoords='offset pixels',
                         xy=(line_scen2.get_xdata()[-1], 
                             line_scen2.get_ydata()[-1]),
                        fontsize=self._style["annotation.fontsize"],
                        arrowprops=dict(
                             color=self._style["dark_gray_color"],
                             arrowstyle="->",
                            connectionstyle="angle3,angleA=-10,angleB=60")
                             )

        ###
        # Legend
        ###

        leg = self.ax.get_legend().remove()
        from matplotlib.lines import Line2D

        #colors = [color_observed, color_scen]
        lines = self.ax.get_lines()[:2]
        labels = ['Historiska utsläpp', 'Utsläppsscenarier']
        self.ax.legend(lines, labels)




