from newsworthycharts import DatawrapperChart
from newsworthycharts.storage import LocalStorage, DictStorage
import os

# store test charts to this folder for visual verfication
OUTPUT_DIR = "test/rendered_charts"
local_storage = LocalStorage(OUTPUT_DIR)
os.environ["DATAWRAPPER_API_KEY"] = "b303a2e8584e4dfe1bb2a36fdb25818ff2dbe88c0ef7cfbb10da9ec2288ac3e0"

def test_type_property():
    container = {}

    chart_obj = {
        "width": 800,
        "height": 600,
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
            "Luleå",
            "Happaranda",
        ],
        "dw_data": {
            "type": "d3-lines",
            "title": "My test chart",
            "metadata": {
                "describe": {
                    "source-name": "Newsworthy",
                    "source-url": "http://www.newsworthy.se",
                }
            }
        },
    }
    # when type="bars"...
    c = DatawrapperChart.init_from(chart_obj, storage=local_storage)
    c.render("basic_dw_chart", "png")
