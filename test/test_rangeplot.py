import json
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
        "title": "Någraer i Stockholm",
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
        "value_labels": "percent_change",
        "highlight": "Göteborg",
        "caption": "Källa: SCB",
    }
    # basic
    c = RangePlot.init_from(chart_obj, storage=local_storage)
    c.render("rangeplot_basic", "png")

    chart_obj = {
        'width': 800,
        'height': 550,
        'bar_orientation': 'vertical',
        'title': 'Kommunerna som byggt ut mest',
        'data': [[
            ['Linköping', 0.9165092081727256],
            ['Motala', 0.7191425063745396],
            ['Boxholm', 0.6777901371894698],
            ['Åtvidaberg', 0.7444888040270786],
            ['Mjölby', 0.8415317087937036],
            ['Finspång', 0.6803263825929283],
            ['Norrköping', 0.8749314885863688],
            ['Söderköping', 0.6856928838951311],
            ['Valdemarsvik', 0.4260911502290813],
            ['Vadstena', 0.6572008113590264],
            ['Ödeshög', 0.4866562009419153],
            ['Kinda', 0.6276641091219096],
            ['Ydre', 0.5035891772501381],
        ], [
            ['Linköping', 0.926389318167769],
            ['Motala', 0.7321403343536614],
            ['Boxholm', 0.6933529195739992],
            ['Åtvidaberg', 0.7604852686308492],
            ['Mjölby', 0.8591338228682751],
            ['Finspång', 0.7010903847886816],
            ['Norrköping', 0.9063393847411126],
            ['Söderköping', 0.7275831353919241],
            ['Valdemarsvik', 0.4814992791926958],
            ['Vadstena', 0.7184197282335179],
            ['Ödeshög', 0.550098231827112],
            ['Kinda', 0.7007360672975815],
            ['Ydre', 0.6478021978021978]
        ]],
        'units': 'percent',
        'labels': ['2018', '2019'],
        'highlight': 'Söderköping',
        'value_labels': 'difference',
    }

    c = RangePlot.init_from(chart_obj, storage=local_storage)
    c.render("rangeplot_percent", "png")


def test_rangeplot_with_double_labeling():
    chart_obj = {
        "width": 800,
        "height": 450,
        "bar_orientation": "vertical",
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
        "value_labels": "both",
        "highlight": "Göteborg",
        "caption": "Källa: SCB",
    }
    # basic
    c = RangePlot.init_from(chart_obj, storage=local_storage)
    c.render("rangeplot_with_double_labeling", "png")


def test_rangeplot_with_long_labels():
    """make sure labels fit and dont overlap y ticks
    """
    with open("test/data/range_plot_with_long_labels.json", "r") as f:
        chart_obj = json.load(f)

    c = RangePlot.init_from(chart_obj, storage=local_storage)
    c.render("rangeplot_with_long_labels", "png")
