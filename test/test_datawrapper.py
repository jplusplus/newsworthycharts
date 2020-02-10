"""Tests chart generation with Datawrapper.
Note that these tests are primarily "visual". Check test/rendered_charts folder
that the generated charts look as expected.
"""
from newsworthycharts import DatawrapperChart
from newsworthycharts.storage import LocalStorage, DictStorage
import os
from copy import deepcopy

# store test charts to this folder for visual verfication
OUTPUT_DIR = "test/rendered_charts"
local_storage = LocalStorage(OUTPUT_DIR)

try:
    DATAWRAPPER_API_KEY = os.environ["DATAWRAPPER_API_KEY"]
except KeyError:
    raise Exception("A 'DATAWRAPPER_API_KEY' must be set to run these test. "
                    "Get it here: https://app.datawrapper.de/account/api-tokens")

TEST_LINE_CHART = {
        "width": 800,
        "height": 0, # 0 for auto height
        "title": "Here is a title from chart obj",
        "data": [
            [
                ["2016-01-01", -2],
                ["2017-01-01", 5],
                ["2018-01-01", 2],
                ["2019-01-01", 2]
            ],
            [
                ["2016-01-01", -4],
                ["2017-01-01", 4],
                ["2018-01-01", 1],
                ["2019-01-01", -1]
            ]
        ],
        "labels": [
            u"Luleå",
            u"Happaranda",
        ],
        "caption": "Ministry of stats",
        "dw_data": {
            "type": "d3-lines",
            "metadata": {
                "describe": {
                    "byline": "Newsworthy"
                }
            }
        },
    }

def test_basic_chart():
    chart_obj = deepcopy(TEST_LINE_CHART)

    c = DatawrapperChart.init_from(chart_obj, storage=local_storage,
                                   language="sv-SE")

    c.render_all("dw_chart_basic")

def test_chart_with_highlight():
    chart_obj = deepcopy(TEST_LINE_CHART)
    chart_obj["highlight"] = "Luleå"

    c = DatawrapperChart.init_from(chart_obj, storage=local_storage,
                                   language="sv-SE")

    c.render_all("dw_chart_with_highlight")

def test_line_chart_with_pct():
    chart_obj = deepcopy(TEST_LINE_CHART)
    chart_obj["units"] = "percent"
    chart_obj["decimals"] = 1
    chart_obj["data"] = [
        [
            ["2016-01-01", -.211],
            ["2017-01-01", .536],
            ["2018-01-01", .213],
            ["2019-01-01", .221]
        ],
        [
            ["2016-01-01", -.431],
            ["2017-01-01", None],
            ["2018-01-01", .118],
            ["2019-01-01", -.136]
        ]
    ]
    c = DatawrapperChart.init_from(chart_obj, storage=local_storage,
                                   language="sv-SE")

    c.render_all("dw_line_chart_with_pct")

def test_vertical_bar_chart_with_highlight():
    chart_obj = deepcopy(TEST_LINE_CHART)
    chart_obj["data"] = [
            [
                ["2016-01-01", -2],
                ["2017-01-01", 5],
                ["2018-01-01", 2],
                ["2019-01-01", 2]
            ],
        ]
    chart_obj["labels"] = ["Luleå"]
    chart_obj["highlight"] = "2019-01-01"
    chart_obj["dw_data"]["type"] = "column-chart"
    c = DatawrapperChart.init_from(chart_obj, storage=local_storage,
                                   language="sv-SE")

    c.render_all("dw_vertical_bar_chart_with_highlight")

def test_horizontal_bar_chart_with_highlight():
    chart_obj = deepcopy(TEST_LINE_CHART)
    chart_obj["data"] = [
            [
                ["Solna", -.221],
                ["Stockholm", .523],
                ["Sundbyberg", .212],
            ],
        ]
    chart_obj["units"] = "percent"
    chart_obj["labels"] = ["Förändring (%)"]
    chart_obj["highlight"] = "Stockholm"
    chart_obj["dw_data"]["type"] = "d3-bars"

    c = DatawrapperChart.init_from(chart_obj, storage=local_storage,
                                   language="sv-SE")

    c.render_all("dw_horizontal_bar_chart_with_highlight")

def test_table():
    chart_obj = {
        "width": 600,
        "height": 0,
        "title": "Några svenska städer jag gillar",
        "labels": ["Kommun", "Värde", "Kategori"],
        "data": [
            {
                "region": "Göteborg",
                "value": 1.1,
                "category": "Västkust",
            },
            {
                "region": "Stockholm",
                "value": 2.1,
                "category": "Östkust",
            },
        ],
        "dw_data": {
            "type": "tables",
        }
    }
    c = DatawrapperChart.init_from(chart_obj, storage=local_storage,
                                   language="sv-SE")

    c.render_all("dw_table")


def test_choropleth_map():
    chart_obj = {
        "width": 400,
        "height": 0,
        "title": "Här är en karta",
        "data": [
            {
                "region": "Västra Götalands län",
                "value": 1.1,
            },
            {
                "region": "Stockholms län",
                "value": 2.1,
            },
            {
                "region": "Skåne län",
                "value": 3.1,
            },
            {
                "region": "Örebro län",
                "value": 6.2,
            }
        ],
        "dw_data": {
            "type": "d3-maps-choropleth",
            "metadata": {
                "axes": {
                    "keys": "region",
                    "values": "value"
                },
                "visualize": {
                    "basemap": "sweden-counties"
                }
            }
        }
    }
    c = DatawrapperChart.init_from(chart_obj, storage=local_storage,
                                   language="sv-SE")

    c.render_all("dw_map_choropleth")
