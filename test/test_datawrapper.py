"""Tests chart generation with Datawrapper.
Note that these tests are primarily "visual". Check tmp/ folder that the
generated charts look as expected.
"""
from newsworthycharts import DatawrapperChart
from newsworthycharts.storage import LocalStorage, DictStorage
import os
from copy import deepcopy

# store test charts to this folder for visual verfication
OUTPUT_DIR = "test/rendered_charts"
local_storage = LocalStorage(OUTPUT_DIR)
os.environ["DATAWRAPPER_API_KEY"] = "b303a2e8584e4dfe1bb2a36fdb25818ff2dbe88c0ef7cfbb10da9ec2288ac3e0"

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
            u"Lule",
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
    chart_obj["highlight"] = "Happaranda"

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
    chart_obj["labels"] = ["Lule"]
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
    chart_obj["labels"] = ["Förändring (%)"]
    chart_obj["highlight"] = "Stockholm"
    chart_obj["dw_data"]["type"] = "d3-bars"

    c = DatawrapperChart.init_from(chart_obj, storage=local_storage,
                                   language="sv-SE")

    c.render_all("dw_horizontal_bar_chart_with_highlight")
