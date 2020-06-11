import pytest
from newsworthycharts import CategoricalChart, CategoricalChartWithReference
from newsworthycharts.storage import LocalStorage

# store test charts to this folder for visual verfication
OUTPUT_DIR = "test/rendered_charts"
local_storage = LocalStorage(OUTPUT_DIR)

def test_bar_orientation():
    chart_obj = {
        "data": [
            [
                ["Stockholm", 321],
                ["Täby", 121],
                ["Solna", None],
            ]
        ],
        "width": 800,
        "height": 600,
        "bar_orientation": "vertical",
        "title": "Några kommuner i Stockholm"
    }
    # 1. Make a vertical chart
    c = CategoricalChart.init_from(chart_obj, storage=local_storage)
    c.render("categorical_chart_vertical", "png")
    bars = c.ax.patches
    assert(bars[0].get_width() < bars[0].get_height())

    # 2. Make a horizontal chart
    chart_obj["bar_orientation"] = "horizontal"
    c = CategoricalChart.init_from(chart_obj, storage=local_storage)
    c.render("categorical_chart_horizontal", "png")
    bars = c.ax.patches
    assert(bars[0].get_width() > bars[0].get_height())

    # 3. Try an invalid bar_orientation
    with pytest.raises(ValueError):
        chart_obj["bar_orientation"] = "foo" #
        c = CategoricalChart.init_from(chart_obj, storage=local_storage)
        c.render("bad_chart", "png")


def test_categorical_chart_with_two_series():
    chart_obj = {
        "data": [
            [
                ["Stockholm", 321],
                ["Täby", 121],
                ["Solna", None],
            ],
            [
                ["Stockholm", 331],
                ["Täby", 151],
                ["Solna", 20],
            ],
        ],
        "labels": ["I år", "I fjol"],
        "width": 800,
        "height": 600,
        "bar_orientation": "vertical",
        "title": "Några kommuner i Stockholm"
    }

    c = CategoricalChartWithReference.init_from(chart_obj, storage=local_storage)
    c.render("categorical_chart_with_two_series", "png")

    # 2. Make a horizontal chart
    chart_obj["bar_orientation"] = "horizontal"
    c = CategoricalChartWithReference.init_from(chart_obj, storage=local_storage)
    c.render("categorical_chart_with_two_series_horizontal", "png")
