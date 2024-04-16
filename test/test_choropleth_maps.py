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


def test_map_with_nw_regions():
    container = {}
    ds = DictStorage(container)

    chart_obj = {
        "width": 800,
        "height": 600,
        "base_map": "se-7-inset",
        "data": [
            [
                ("Stockholms kommun", 3),
                ("Ystads kommun", 2),
                ("Årjängs kommun", 1),
            ]
        ],
    }
    c = ChoroplethMap.init_from(chart_obj, storage=ds)
    c.render("map_with_nw_ids", "png")


def test_map_with_nw_regions_and_subsets():
    container = {}
    ds = DictStorage(container)

    chart_obj = {
        "width": 800,
        "height": 600,
        "base_map": "se|03-7",
        "data": [
            [
                ("Uppsala kommun", 3),
                ("Enköpings kommun", 2),
            ]
        ],
    }
    c = ChoroplethMap.init_from(chart_obj, storage=ds)
    c.render("map_with_nw_ids", "png")


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
