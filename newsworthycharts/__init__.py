__version__ = "1.41.0-rc1"

from .chart import Chart
from .choroplethmap import ChoroplethMap
from .serialchart import SerialChart
from .seasonalchart import SeasonalChart
from .categoricalchart import CategoricalChart, CategoricalChartWithReference, ProgressChart
from .scatterplot import ScatterPlot
from .datawrapper import DatawrapperChart
from .rangeplot import RangePlot
from .custom.climate_cars import ClimateCarsYearlyEmissionsTo2030, ClimateCarsCO2BugdetChart
from .storage import *

CHART_ENGINES = {
    "Chart": Chart,
    "SerialChart": SerialChart,
    "SeasonalChart": SeasonalChart,
    "CategoricalChart": CategoricalChart,
    "CategoricalChartWithReference": CategoricalChartWithReference,
    "ProgressChart": ProgressChart,
    "RangePlot": RangePlot,
    "ScatterPlot": ScatterPlot,
    "DatawrapperChart": DatawrapperChart,
    "ChoroplethMap": ChoroplethMap,

    # custom
    "ClimateCarsYearlyEmissionsTo2030": ClimateCarsYearlyEmissionsTo2030,
    "ClimateCarsCO2BugdetChart": ClimateCarsCO2BugdetChart,
}
