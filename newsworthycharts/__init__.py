__version__ = "1.52.8"

from .chart import Chart
from .choroplethmap import ChoroplethMap
from .bubblemap import BubbleMap
from .serialchart import SerialChart
from .seasonalchart import SeasonalChart
from .categoricalchart import CategoricalChart, CategoricalChartWithReference, ProgressChart
from .scatterplot import ScatterPlot
from .datawrapper import DatawrapperChart
from .rangeplot import RangePlot
from .stripechart import StripeChart
from .custom.climate_cars import ClimateCarsYearlyEmissionsTo2030, ClimateCarsCO2BugdetChart
from .storage import *

CHART_ENGINES = {
    "BubbleMap": BubbleMap,
    "CategoricalChart": CategoricalChart,
    "CategoricalChartWithReference": CategoricalChartWithReference,
    "Chart": Chart,
    "ChoroplethMap": ChoroplethMap,
    "DatawrapperChart": DatawrapperChart,
    "ProgressChart": ProgressChart,
    "RangePlot": RangePlot,
    "ScatterPlot": ScatterPlot,
    "SeasonalChart": SeasonalChart,
    "SerialChart": SerialChart,
    "StripeChart": StripeChart,

    # custom
    "ClimateCarsYearlyEmissionsTo2030": ClimateCarsYearlyEmissionsTo2030,
    "ClimateCarsCO2BugdetChart": ClimateCarsCO2BugdetChart,
}
