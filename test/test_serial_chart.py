from newsworthycharts import SerialChart
from newsworthycharts.storage import DictStorage, LocalStorage


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
    lines = c.ax.patches
    # ... should only render one element
    # assert(len(lines) == 1)
