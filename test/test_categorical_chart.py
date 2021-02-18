import pytest
from newsworthycharts import CategoricalChart, CategoricalChartWithReference, ProgressChart
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


def test_bar_highlight():
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
        "highlight": "Stockholm",
        "bar_orientation": "vertical",
        "title": "Några kommuner i Stockholm"
    }
    c = CategoricalChart.init_from(chart_obj, storage=local_storage)
    c.render("categorical_chart_with_highlight", "png")

def test_stacked_categorical_chart():
    chart_obj = {
        "data": [
            [
                ["Stockholm", 321],
                ["Täby", 121],
                ["Solna", None],
            ],
            [
                ["Stockholm", 131],
                ["Täby", 151],
                ["Solna", 120],
            ],
        ],
        "labels": ["Snabba", "Långsamma"],
        "width": 800,
        "height": 600,
        "stacked": True,
        "highlight": "Långsamma",
        "bar_orientation": "vertical",
        "title": "Några kommuner i Stockholm"
    }
    # 1. Make a vertical stacked chart
    c = CategoricalChart.init_from(chart_obj, storage=local_storage)
    c.render("categorical_chart_stacked", "png")

    # 2.Make a horizontal stacked chart
    chart_obj["bar_orientation"] = "horizontal"
    c = CategoricalChart.init_from(chart_obj, storage=local_storage)
    c.render("categorical_chart_stacked_horizontal", "png")

def test_categorical_chart_with_reference_series():
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


def test_progress_chart():

    chart_obj = {
        "data": [
            [
                ("Stockholms län"	, .9404),
                ("Gotlands län"	, .8868),
                ("Västra Götalands län"	, .8260),
                ("Hallands län"	, .8193),
                ("Västerbottens län"	, .7974),
                ("Skåne län"	, .7746),
                ("Östergötlands län"	, .7639),
                ("Jönköpings län"	, .7617),
                ("Värmlands län"	, .7612),
                ("Västmanlands län"	, .7578),
                ("Södermanlands län"	, .7536),
                ("Gävleborgs län"	, .7468),
                ("Kronobergs län"	, .7306),
                ("Uppsala län"	, .7204),
                ("Örebro län"	, .7176),
                ("Blekinge län"	, .6918),
                ("Norrbottens län"	, .6830),
                ("Dalarnas län"	, .6719),
                ("Hallands län"	, .6650),
                ("Västernorrlands län"	, .6546),
                ("Kalmar län"	, .6332),
            ],
        ],
        "target": .95,
        "target_label": "Mål: 95 %",
        "labels": ["Täckning i dag", "Kvar till målet"],
        "value_labels": "progress",
        "width": 600,
        "height": 900,
        "units": "percent",
        "bar_orientation": "horizontal",
        "title": "Inga regioner klarar målet"
    }
    c = ProgressChart.init_from(chart_obj, storage=local_storage)

    c.render("progress_chart", "png")
