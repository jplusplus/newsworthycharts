from newsworthycharts import ScatterPlot
from newsworthycharts.storage import LocalStorage
from .data.scatterplot import income_vs_evs

# store test charts to this folder for visual verfication
OUTPUT_DIR = "test/rendered_charts"
local_storage = LocalStorage(OUTPUT_DIR)


def test_basic_scatterplot():

    chart_obj = {
        "width": 800,
        "height": 600,
        "data": [
            [
                [.1, 3, "Stockholm"],
                [.32, 4, "Solna"],
                [.45, 7, "Sundbyberg"],
                [.67, 5, "Huddinge"],
            ]
        ],
        "units_x": "percent",
        "xlabel": "Andel nånting",
        "ylabel": "Antal av nåt annat",
        "highlight": ["Stockholm"],
        "title": "Vilket slående samband!"
    }
    c = ScatterPlot.init_from(chart_obj, storage=local_storage)
    c.render("scatterplot-basic", "png")


def test_large_scatterplot():

    chart_obj = {
        "width": 800,
        "height": 600,
        "data": [income_vs_evs],
        "units_y": "percent",
        "xlabel": "Disp. inkomst",
        "ylabel": "Andel laddbara\nbilar",
        "ymin": 0,
        "highlight": ["Stockholms kommun"],
        "labels": [
            'Danderyd', 'Lidingö', 'Lomma', 'Mölndal', 'Nacka',
            'Solna', 'Stockholms kommun', 'Södertälje',
        ],
        "title": "Vilket slående samband!"
    }
    c = ScatterPlot.init_from(chart_obj, storage=local_storage)
    c.render("scatterplot-munis", "png")
