"""Tests chart generation with Datawrapper.
Note that these tests are primarily "visual". Check test/rendered_charts folder
that the generated charts look as expected.
"""
from newsworthycharts import DatawrapperChart
from newsworthycharts.storage import LocalStorage
import os
from copy import deepcopy
from dotenv import load_dotenv
load_dotenv()

# store test charts to this folder for visual verfication
OUTPUT_DIR = "test/rendered_charts"
local_storage = LocalStorage(OUTPUT_DIR)

try:
    DATAWRAPPER_API_KEY = os.environ["DATAWRAPPER_API_KEY"]
except KeyError:
    raise Exception("A 'DATAWRAPPER_API_KEY' must be set to run these test. "
                    "Get it here: https://app.datawrapper.de/account/api-tokens")

TEST_LINE_CHART = {
    "width": 800,
    "height": 0,  # 0 for auto height
    "title": "Here is a title from chart obj",
    "data": [
        [
            ["2016-01-01", -2],
            ["2017-01-01", 5],
            ["2018-01-01", 2],
            ["2019-01-01", 2]
        ],
        [
            ["2016-01-01", -4],
            ["2017-01-01", 4],
            ["2018-01-01", 1],
            ["2019-01-01", -1]
        ]
    ],
    "labels": [
        u"Luleå",
        u"Happaranda",
    ],
    "caption": "Ministry of stats",
    "dw_data": {
        "type": "d3-lines",
        "metadata": {
            "describe": {
                "byline": "Newsworthy"
            }
        }
    },
}


def test_basic_chart():
    chart_obj = deepcopy(TEST_LINE_CHART)

    c = DatawrapperChart.init_from(chart_obj, storage=local_storage,
                                   language="sv-SE")

    c.render_all("dw_chart_basic")


def test_chart_with_highlight():
    chart_obj = deepcopy(TEST_LINE_CHART)
    chart_obj["highlight"] = "Luleå"

    c = DatawrapperChart.init_from(chart_obj, storage=local_storage,
                                   language="sv-SE")

    c.render_all("dw_chart_with_highlight")


def test_line_chart_with_pct():
    chart_obj = deepcopy(TEST_LINE_CHART)
    chart_obj["units"] = "percent"
    chart_obj["decimals"] = 1
    chart_obj["data"] = [
        [
            ["2016-01-01", -.211],
            ["2017-01-01", .536],
            ["2018-01-01", .213],
            ["2019-01-01", .221]
        ],
        [
            ["2016-01-01", -.431],
            ["2017-01-01", None],
            ["2018-01-01", .118],
            ["2019-01-01", -.136]
        ]
    ]
    c = DatawrapperChart.init_from(chart_obj, storage=local_storage,
                                   language="sv-SE")

    c.render_all("dw_line_chart_with_pct")


def test_vertical_bar_chart_with_highlight():
    chart_obj = deepcopy(TEST_LINE_CHART)
    chart_obj["data"] = [
        [
            ["2016-01-01", -2],
            ["2017-01-01", 5],
            ["2018-01-01", 2],
            ["2019-01-01", 2]
        ],
    ]
    chart_obj["labels"] = ["Luleå"]
    chart_obj["highlight"] = "2019-01-01"
    chart_obj["dw_data"]["type"] = "column-chart"
    c = DatawrapperChart.init_from(chart_obj, storage=local_storage,
                                   language="sv-SE")

    c.render_all("dw_vertical_bar_chart_with_highlight")


def test_horizontal_bar_chart_with_highlight():
    chart_obj = deepcopy(TEST_LINE_CHART)
    chart_obj["data"] = [
        [
            ["Solna", -.221],
            ["Stockholm", .523],
            ["Sundbyberg", .212],
        ],
    ]
    chart_obj["units"] = "percent"
    chart_obj["labels"] = ["Förändring (%)"]
    chart_obj["highlight"] = "Stockholm"
    chart_obj["dw_data"]["type"] = "d3-bars"

    c = DatawrapperChart.init_from(chart_obj, storage=local_storage,
                                   language="sv-SE")

    c.render_all("dw_horizontal_bar_chart_with_highlight")


def test_table():
    chart_obj = {
        "width": 600,
        "height": 0,
        "title": "Några svenska städer jag gillar",
        "labels": ["Kommun", "Värde", "Kategori"],
        "data": [
            {
                "region": "Göteborg",
                "value": 1.1,
                "category": "Västkust",
            },
            {
                "region": "Stockholm",
                "value": 2.1,
                "category": "Östkust",
            },
        ],
        "dw_data": {
            "type": "tables",
        }
    }
    c = DatawrapperChart.init_from(chart_obj, storage=local_storage,
                                   language="sv-SE")

    c.render_all("dw_table")


def test_choropleth_map():
    chart_obj = {
        "width": 400,
        "height": 500,
        "title": "Här är en karta",
        "data": [
            {
                "region": "Västra Götalands län",
                "value": 1.1,
            },
            {
                "region": "Stockholms län",
                "value": 2.1,
            },
            {
                "region": "Skåne län",
                "value": 3.1,
            },
            {
                "region": "Örebro län",
                "value": 6.2,
            }
        ],
        "dw_data": {
            "type": "d3-maps-choropleth",
            "metadata": {
                "axes": {
                    "keys": "region",
                    "values": "value"
                },
                "visualize": {
                    "basemap": "sweden-counties"
                }
            }
        }
    }
    c = DatawrapperChart.init_from(chart_obj, storage=local_storage,
                                   language="sv-SE")

    c.render_all("dw_map_choropleth")


def test_pie_chart():
    metadata = {
        'data': {
            'transpose': False,
            'vertical-header': True,
            'horizontal-header': True
        },
        'publish': {
            'embed-width': 600,
            'chart-height': 330,
            'embed-height': 415
        },
        'annotate': {'notes': ''},
        'describe': {
            'intro': '',
            'byline': '',
            'source-url': '',
            'source-name': '',
            'number-append': '',
            'number-format': '-',
            'number-divisor': 0,
            'number-prepend': '',
        },
        'visualize': {
            'group': {'text': 'Other', 'num_slices': 5},
            'x-grid': 'off',
            'y-grid': 'on',
            'scale-y': 'linear',
            'labeling': 'right',
            'pie_size': {'inside_labels': 75, 'outside_labels': 50},
            'color_key': {
                'stack': False,
                'enabled': False,
                'position': 'top',
                'label_values': False,
            },
            'base-color': 0,
            'base_color': 0,
            'fill-below': False,
            'line-dashes': [],
            'line-widths': [],
            'slice_order': 'descending',
            'fill-between': False,
            'label-colors': False,
            'label-margin': 0,
            'line-symbols': False,
            'show_percent': False,
            'custom-colors': {
                'Möjligen bokningsbara': 6,
                'Bekfräftat tillgängliga': 5,
            },
            'inside_labels': {'enabled': False},
            'interpolation': 'linear',
            'show-tooltips': True,
            'x-tick-format': 'YYYY',
            'y-grid-format': '0,0.[00]',
            'y-grid-labels': 'auto',
            'chart-type-set': True,
            'custom-range-x': ['', ''],
            'custom-range-y': ['', ''],
            'custom-ticks-x': '',
            'custom-ticks-y': '',
            'outside_labels': {'edge': False, 'color': False, 'enabled': True},
            'rotation_angle': 0,
            'connector-lines': True,
            'donut_hole_size': 50,
            'line-symbols-on': 'both',
            'small_multiples': {
                'group_value_label': {
                    'type': 'total',
                    'enabled': False,
                    'total_text': 'Total',
                    'single_selected_row': 0,
                },
                'min_col_grid_width': 120,
            },
            'y-grid-subdivide': True,
            'custom-area-fills': [],
            'label_text_slices': True,
            'line-symbols-size': 3.5,
            'line-value-labels': False,
            'donut_center_label': {
                'type': 'total',
                'enabled': False,
                'total_text': 'Total',
                'custom_text': '',
                'single_selected_row': 0,
            },
            'highlighted-series': [],
            'highlighted-values': [],
            'line-symbols-shape': 'circle',
            'value-label-format': '0,0.[00]',
            'y-grid-label-align': 'left',
            'label_values_slices': True,
            'line-symbols-opacity': 1,
            'area-fill-color-below': '#cccccc',
            'tooltip-number-format': '0,0.[00]',
            'area-fill-color-between': '#cccccc',
            'line-symbols-shape-multiple': []
        },
        'json_error': None,
    }
    chart_obj = {
        "data": [
            {
                "key": 'Möjligen bokningsbara',
                "value": 35,
            },
            {
                "key": 'Bekfräftat tillgängliga',
                "value": 65
            }
        ],
        "width": 400,
        "height": 300,
        "dw_data": {
            "type": 'd3-donuts',
            "metadata": metadata,
        }
    }
    c = DatawrapperChart.init_from(chart_obj, storage=local_storage,
                                   language="sv-SE")
    c.render("dw_pie1", "png")


def test_pie_chart2():
    chart_obj = {
        'width': 380, 'height': 250,
        'format': 'png',
        'theme': 'newsworthy',
        'lang': 'sv',
        'overwrite': False,
        'chart_engine': 'DatawrapperChart',
        'data': [
            {
                'key': 'Möjligen boknings- bara',
                'value': 0.7186602152835304
            }, {
                'key': 'Tillgängliga', 'value': 0.2813397847164696
            }
        ],
        'datatype': None,
        'decimals': 0,
        'dw_data': {
            'metadata': {
                'visualize': {
                    'custom-colors': {
                        'Möjligen boknings- bara': '#cdcdcd',
                        'Tillgängliga': '#5aa69d',
                    },
                    'donut_hole_size': 50,
                    'inside_labels': {'enabled': False},
                    'line-symbols-size': 6.5,
                    'outside_labels': {
                        'color': False,
                        'edge': False,
                        'enabled': True,
                    },
                    'pie_size': {
                        'inside_labels': 75,
                        'outside_labels': 50,
                    },
                    'slice_order': 'original',
                    'value-label-format': '0%',
                }
            },
            'type': 'd3-donuts'
        },
        'labels': [],
        'series': [],
        'source': None,
        'type': 'bars',
        'units': 'percent',
        'title': None,
        'key': '2837248355',
        'language': 'sv',
        'style': 'newsworthy',
        'primary_color': '#5aa69d',
        'size': 'normal',
        'bar_orientation':
        'horizontal',
        'show_category_ticks': True,
        'ymin': 0,
        'ticks': 'yearly',
        'highlight_change': False
    }
    c = DatawrapperChart.init_from(chart_obj, storage=local_storage,
                                   language="sv-SE")
    c.render("dw_pie_test", "png")
