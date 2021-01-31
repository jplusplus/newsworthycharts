from .chart import Chart
from .serialchart import SerialChart
from .categoricalchart import CategoricalChart, CategoricalChartWithReference
from .scatterplot import ScatterPlot
from .datawrapper import DatawrapperChart
from .custom.climate_cars import ClimateCarsYearlyEmissionsTo2030
from .storage import *

CHART_ENGINES = {
    "Chart": Chart,
    "SerialChart": SerialChart,
    "CategoricalChart": CategoricalChart,
    "CategoricalChartWithReference": CategoricalChartWithReference,
    "ScatterPlot": ScatterPlot,
    "DatawrapperChart": DatawrapperChart,
    "ClimateCarsYearlyEmissionsTo2030": ClimateCarsYearlyEmissionsTo2030,
}
