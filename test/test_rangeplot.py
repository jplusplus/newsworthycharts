import pytest
from newsworthycharts import RangePlot
from newsworthycharts.storage import LocalStorage

# store test charts to this folder for visual verfication
OUTPUT_DIR = "test/rendered_charts"
local_storage = LocalStorage(OUTPUT_DIR)

def test_basic_rangeplot():
    chart_obj = {
        "width": 800,
        "height": 450,
        "bar_orientation": "vertical",
        "title": "Några kommuner i Stockholm",
        "subtitle": "Antal grejer som finns kvar efter en stor händelse.",
        "data": [
            [
                ("Stockholm", 10), 
                ("Göteborg", 8), 
                ("Malmö", 4),
            ],
            [
                ("Stockholm", 7), 
                ("Göteborg", 11), 
                ("Malmö", -3),
            ],
        ],
        "labels": ["Före", "Efter"],
        "values_labels": "percent_change",
        "highlight": "Göteborg",
        "caption": "Källa: SCB" 
    }
    # 1. Make a vertical chart
    c = RangePlot.init_from(chart_obj, storage=local_storage)
    c.render("rangeplot_basic", "png")
