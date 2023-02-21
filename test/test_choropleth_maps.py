from newsworthycharts import ChoroplethMap
from newsworthycharts.storage import DictStorage, LocalStorage
import pytest

# store test charts to this folder for visual verfication
OUTPUT_DIR = "test/rendered_charts"
local_storage = LocalStorage(OUTPUT_DIR)


def test_rendering():
    container = {}
    ds = DictStorage(container)

    chart_obj = {
        "width": 800,
        "height": 600,
        "base_map": "se-7",
        "data": [
            [
                ("SE-0180", 3)
            ]
        ],
    }
    c = ChoroplethMap.init_from(chart_obj, storage=ds)
    c.render("test", "png")


def test_invalid_region():
    container = {}
    ds = DictStorage(container)

    chart_obj = {
        "width": 800,
        "height": 600,
        "base_map": "se-7",
        "data": [
            [
                ("SE-qwrety", 3)
            ]
        ],
    }
    with pytest.raises(ValueError):
        c = ChoroplethMap.init_from(chart_obj, storage=ds)
        c.render("test", "png")
