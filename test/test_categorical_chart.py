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
    assert bars[0].get_width() < bars[0].get_height()

    # 2. Make a horizontal chart
    chart_obj["bar_orientation"] = "horizontal"
    c = CategoricalChart.init_from(chart_obj, storage=local_storage)
    c.render("categorical_chart_horizontal", "png")
    bars = c.ax.patches
    assert bars[0].get_width() > bars[0].get_height()

    # 3. Try an invalid bar_orientation
    with pytest.raises(ValueError):
        chart_obj["bar_orientation"] = "foo"
        c = CategoricalChart.init_from(chart_obj, storage=local_storage)
        c.render("bad_chart", "png")


def test_tall_chart():
    chart_obj = {
        "data": [
            [
                ('Strömstad', -0.084),
                ('Lysekil', -0.023),
                ('Bengtsfors', -0.021),
                ('Sotenäs', -0.019),
                ('Dals-Ed', -0.018),
                ('Mellerud', -0.014),
                ('Trollhättan', -0.013),
                ('Gullspång', -0.013),
                ('Götene', -0.013),
                ('Vänersborg', -0.013),
                ('Grästorp', -0.013),
                ('Färgelanda', -0.012),
                ('Partille', -0.012),
                ('Tjörn', -0.011),
                ('Töreboda', -0.01),
                ('Svenljunga', -0.009),
                ('Öckerö', -0.008),
                ('Tanum', -0.008),
                ('Göteborg', -0.007),
                ('Falköping', -0.007),
                ('Skara', -0.007),
                ('Tidaholm', -0.007),
                ('Uddevalla', -0.006),
                ('Herrljunga', -0.006),
                ('Hjo', -0.005),
                ('Mark', -0.005),
                ('Bollebygd', -0.005),
                ('Härryda', -0.004),
                ('Vara', -0.004),
                ('Essunga', -0.003),
                ('Mölndal', -0.004),
                ('Karlsborg', -0.002),
                ('Orust', -0.002),
                ('Skövde', -0.002),
                ('Tranemo', -0.001),
                ('Alingsås', -0.0),
                ('Borås', -0.0),
                ('Tibro', 0.001),
                ('Stenungsund', 0.001),
                ('Lidköping', 0.001),
                ('Åmål', 0.002),
                ('Ale', 0.002),
                ('Lerum', 0.003),
                ('Lilla Edet', 0.003),
                ('Ulricehamn', 0.004),
                ('Vårgårda', 0.004),
                ('Mariestad', 0.006),
                ('Kungälv', 0.007),
                ('Munkedal', 0.007)
            ]
        ],
        "width": 600,
        "height": 1900,
        "bar_orientation": "horizontal",
        "title": "Oj vad det finns många kommuner i Västra Götland",
        "subtitle": "Se till så att de får plats.",
        "note": "Här kommer en anteckning. Och verifiera att den här faktiskt kan gå över två rader utan att det blir nåt problem.",  # NOQA
    }
    c = CategoricalChart.init_from(chart_obj, storage=local_storage)
    c.render("categorical_chart_tall", "png")


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
    bar_sthlm, bar_täby, bar_solna = c.ax.patches

    assert bar_sthlm.get_fc() == c._nwc_style["strong_color"]
    assert bar_täby.get_fc() == c._nwc_style["neutral_color"]

    # Render multiple
    chart_obj["highlight"] = ["Täby", "Stockholm"]
    c = CategoricalChart.init_from(chart_obj, storage=local_storage)
    c.render("categorical_chart_with_mulitple_highlights", "png")
    bar_sthlm, bar_täby, bar_solna = c.ax.patches
    assert bar_sthlm.get_fc() == c._nwc_style["strong_color"]
    assert bar_täby.get_fc() == c._nwc_style["strong_color"]


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


def test_colored_categorical_chart_with_reference_series():
    chart_obj = {
        "data": [
            [
                ('M', 0.1985116137263444),
                ('S', 0.2839164376430766),
                ('L', 0.0542573269504105),
                ('C', 0.0870201872782123),
                ('V', 0.0771319115248597),
                ('MP', 0.0431621625601214),
                ('KD', 0.0634608272219474),
                ('SD', 0.1778209311248905),
            ],
            [
                ('M', 0.233),
                ('S', 0.31),
                ('L', 0.054000000000000006),
                ('C', 0.061),
                ('V', 0.057),
                ('MP', 0.069),
                ('KD', 0.046),
                ('SD', 0.129),
            ],
        ],
        "colors": [
            '#6295c3',
            '#da373d',
            '#446793',
            '#285f35',
            '#973933',
            '#669e51',
            '#323e72',
            '#ddb647'
        ],
        "legend": False,
        "labels": ["2018", "2014"],
        "width": 800,
        "height": 600,
        "units": "percent",
        "bar_orientation": "vertical",
        "title": "Partiernas valresultat 2018"
    }

    c = CategoricalChartWithReference.init_from(chart_obj, storage=local_storage)
    c.render("categorical_chart_with_reference_colored", "png")


def test_categorical_chart_with_reference_and_highlight():
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
        "highlight": ["Täby"],
        "bar_orientation": "vertical",
        "title": "Kolla på Täby här"
    }

    c = CategoricalChartWithReference.init_from(chart_obj, storage=local_storage)
    c.render("categorical_chart_with_reference_and_highlight", "png")


def test_progress_chart():

    chart_obj = {
        "data": [
            [
                ("Stockholms län", .9604, ">95 %"),
                ("Gotlands län", .8868),
                ("Västra Götalands län", .8260),
                ("Hallands län", .8193),
                ("Västerbottens län", .7974),
                ("Skåne län", .7746),
                ("Östergötlands län", .7639),
                ("Jönköpings län", .7617),
                ("Värmlands län", .7612),
                ("Västmanlands län", .7578),
                ("Södermanlands län", .7536),
                ("Gävleborgs län", .7468),
                ("Kronobergs län", .7306),
                ("Uppsala län", None),
                ("Örebro län", None),
                ("Blekinge län", .6918),
                ("Norrbottens län", .6830),
                ("Dalarnas län", .6719),
                ("Hallands län", .6650),
                ("Västernorrlands län", .6546),
                ("Kalmar län", .6332),
            ],
        ],
        "legend": False,
        "target": .95,
        "target_label": "Mål: 95 %",
        "labels": ["Täckning i dag", "Kvar till målet"],
        "value_labels": "progress",
        "width": 600,
        "height": 900,
        "units": "percent",
        "highlight": "Kalmar län",
        "bar_orientation": "horizontal",
        "title": "Inga regioner klarar målet"
    }
    c = ProgressChart.init_from(chart_obj, storage=local_storage)

    c.render("progress_chart", "png")


def test_progress_chart_with_multiple_targets():
    chart_obj = {
        "data": [
            [
                ("30 Mbit/s", .9404),
                ("100 Mbit/s", .8868),
                ("1 Gbit/s", .8260),
            ],
        ],
        "target": [1, .99, .95],
        "value_labels": "progress",
        "width": 700,
        "height": 400,
        "units": "percent",
        "bar_orientation": "horizontal",
        "title": "Inga mål uppnås"
    }
    c = ProgressChart.init_from(chart_obj, storage=local_storage)

    c.render("progress_chart_with_multiple_targets", "png")
