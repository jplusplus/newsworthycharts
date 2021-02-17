from newsworthycharts import SerialChart
from newsworthycharts.storage import DictStorage, LocalStorage

# store test charts to this folder for visual verfication
OUTPUT_DIR = "test/rendered_charts"
local_storage = LocalStorage(OUTPUT_DIR)


def test_color_function():
    container = {}
    ds = DictStorage(container)

    chart_obj = {
        "width": 800,
        "height": 600,
        "data": [
            [
                ["2016-01-01", -4],
                ["2017-01-01", 4],
                ["2018-01-01", None],
                ["2019-01-01", -1]
            ]
        ],
        "type": "bars",
        "color_fn": "positive_negative",
        "highlight": "2019-01-01",
    }
    c = SerialChart.init_from(chart_obj, storage=ds)
    c.render("test", "png")

    neutral_color = c._style["neutral_color"]
    pos_color = c._style["positive_color"]
    neg_color = c._style["negative_color"]
    bar_colors = [bar.get_facecolor() for bar in c.ax.patches]
    assert(bar_colors[0] == neg_color)
    assert(bar_colors[1] == pos_color)
    assert(bar_colors[2] == neutral_color)
    assert(bar_colors[3] == neg_color)

    chart_obj["color_fn"] = "warm_cold"
    c = SerialChart.init_from(chart_obj, storage=ds)
    c.render("test", "png")

    warm_color = c._style["warm_color"]
    cold_color = c._style["cold_color"]
    bar_colors = [bar.get_facecolor() for bar in c.ax.patches]

    assert(bar_colors[0] == cold_color)
    assert(bar_colors[1] == warm_color)
    assert(bar_colors[2] == neutral_color)
    assert(bar_colors[3] == cold_color)


def test_type_property():
    container = {}
    ds = DictStorage(container)

    chart_obj = {
        "width": 800,
        "height": 600,
        "data": [
            [
                ["2016-01-01", -4],
                ["2017-01-01", 4],
                ["2018-01-01", 1],
                ["2019-01-01", -1]
            ]
        ],
        "type": "bars",
    }
    # when type="bars"...
    c = SerialChart.init_from(chart_obj, storage=ds)
    c.render("test", "png")
    bars = c.ax.patches
    # ...4 bars should be rendered
    assert(len(bars) == 4)

    # while a type=line...
    chart_obj["type"] = "line"
    c = SerialChart.init_from(chart_obj, storage=ds)
    c.render("test", "png")
    #lines = c.ax.patches
    # ... should only render one element
    # assert(len(lines) == 1)

def test_stacked_bar_chart():
    chart_obj = {
        "width": 800,
        "height": 600,
        "data": [
            [
                ["2016-01-01", 1],
                ["2017-01-01", 4],
                ["2018-01-01", None],
                ["2019-01-01", 2]
            ],
            [
                ["2016-01-01", 3],
                ["2017-01-01", 12],
                ["2018-01-01", 1],
                ["2019-01-01", None]
            ]
        ],
        "labels": ["the good", "the bad"],
        "type": "bars",
    }
    # when type="bars"...
    c = SerialChart.init_from(chart_obj, storage=local_storage)
    c.render("stacked_bar_chart_basic", "png")
    bars = c.ax.patches
    assert(len(bars) == 8)

    # Should color with qualitative colors by default
    qualitative_colors = c._style["qualitative_colors"]
    bar_colors = [bar.get_facecolor() for bar in c.ax.patches]
    assert(bar_colors[0] == qualitative_colors[0])
    assert(bar_colors[-1] == qualitative_colors[1])

    # now highlight
    chart_obj["highlight"] = "the good"
    c = SerialChart.init_from(chart_obj, storage=local_storage)
    c.render("stacked_bar_chart_highlighted", "png")
    bar_colors = [bar.get_facecolor() for bar in c.ax.patches]
    assert(bar_colors[0] == c._style["strong_color"])
    assert(bar_colors[-1] == c._style["neutral_color"])


def test_bar_chart_with_ymax():
    container = {}
    ds = DictStorage(container)

    # all negative values with fixed ymax to 0
    chart_obj = {
        "width": 800,
        "height": 600,
        "data": [
            [
                ["2016-01-01", -4],
                ["2017-01-01", -6],
                ["2018-01-01", -3],
                ["2019-01-01", -2]
            ]
        ],
        "ymax": 0,
        "type": "bars",
    }
    c = SerialChart.init_from(chart_obj, storage=local_storage)
    c.render("bar_chart_with_ymax1", "png")
    assert c.ax.get_ylim()[1] == 0

    # when ymax < actual max value in data
    chart_obj = {
        "width": 800,
        "height": 600,
        "data": [
            [
                ["2016-01-01", 4],
                ["2017-01-01", 6],
                ["2018-01-01", 3],
                ["2019-01-01", 2]
            ]
        ],
        "ymax": 3,
        "type": "bars",
    }
    c = SerialChart.init_from(chart_obj, storage=local_storage)
    c.render("bar_chart_with_ymax2", "png")
    max_value = max([x[1] for x in chart_obj["data"][0]])
    assert c.ax.get_ylim()[1] > max_value

def test_chart_with_long_y_ticks():
    chart_obj = {
        "width": 800,
        "height": 600,
        "data": [
            [
                ["2016-01-01", 4e6],
                ["2017-01-01", 6e6],
                ["2018-01-01", 3e6],
                ["2019-01-01", 2e6]
            ]
        ],
        "title": "Look how large numbers!",
        "type": "bars",
    }
    c = SerialChart.init_from(chart_obj, storage=local_storage)
    # visually make sure tick labels are visible
    c.render("serial_bar_chart_with_long_y_ticks", "png")


def test_weekly_chart():
    container = {}
    ds = DictStorage(container)

    # all negative values with fixed ymax to 0
    chart_obj = {
        "width": 800,
        "height": 600,
        "data": [
            [
                [ "2020-06-22", 0.391 ],
                [ "2020-06-29", 0.346 ],
                [ "2020-07-06", 0.297 ],
                [ "2020-07-13", 0.317 ],
                [ "2020-07-20", 0.197 ],
                [ "2020-07-27", 0.417 ],
            ]
        ],
        "type": "bars",
        "units": "percent",
        "interval": "weekly",
    }
    c = SerialChart.init_from(chart_obj, storage=local_storage)
    c.render("serial_chart_weekly", "png")

def test_multi_color_lines():
    colors =  ["red", "green", "blue"]

    chart_obj = {
        "width": 800,
        "height": 600,
        "data": [
            [
                ["2017-01-01", -6],
                ["2018-01-01", -3],
                ["2019-01-01", -2]
            ],
            [
                ["2017-01-01", -3],
                ["2018-01-01", -1],
                ["2019-01-01", 4]
            ], 
            [
                ["2017-01-01", 2],
                ["2018-01-01", 5],
                ["2019-01-01", -3]
            ]

        ],
        "labels": colors, 
        "colors": colors,
        "ymax": 0,
        "type": "line",
    }
    c = SerialChart.init_from(chart_obj, storage=local_storage)
    c.render("serial_chart_multi_color", "png")
    for i, color in enumerate(colors):
        assert c.ax.get_lines()[i].get_color() == color
    
