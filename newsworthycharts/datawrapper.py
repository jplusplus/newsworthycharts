from babel import Locale
import os
from langcodes import standardize_tag
import requests
from copy import deepcopy
from io import BytesIO, StringIO
import csv
from matplotlib.colors import rgb2hex

from .storage import Storage, LocalStorage
from .chart import Chart
from .lib.utils import loadstyle
from .lib.datalist import DataList

HERE = os.path.dirname(__file__)


class DatawrapperChart(Chart):
    # TODO: Make file_types dynami. Available file types depend on the
    # account level. png is available at all levels.
    file_types = ["png"]

    def __init__(self, width: int, height: int, storage: Storage=LocalStorage(),
                 style: str='newsworthy', language: str='en-GB'):
        """
        :param width: width in pixels
        :param height: height in pixels
        :param storage: storage object that will handle file saving. Default
                        LocalStorage() class will save a file the working dir.
        :param style: a predefined style or the path to a custom style file
        :param language: a BCP 47 language tag (eg `en`, `sv-FI`)
        """
        try:
            self.api_token = os.environ["DATAWRAPPER_API_KEY"]
        except KeyError:
            raise Exception("DATAWRAPPER_API_KEY must be set in environment")

        # P U B L I C   P R O P E R T I E S
        # The user can alter these at any time

        # Unlike regular Chart objects Datawrapper does not use the DataList
        # class for storing data, as DataList does not handle non-numerical
        # data. DatawrapperCharts will understand the same list-of-list-of-list
        # structure as DataList builds upon, but prefer consuming list of
        # dictionaries
        self.data = []
        self.labels = []  # Optionally one label for each dataset
        self.annotations = []  # Manually added annotations
        self.caption = None
        self.highlight = None
        self.decimals = None

        self.dw_data = {}  # The DW data structure that defines the chart
        self._dw_id = None  # Datawrapper chart id

        #  P R I V A T E   P R O P E R T I E S
        #  Properties managed through getters/setters
        self._title = None
        self._units = "count"

        # Calculated properties
        self._storage = storage
        self._w, self._h = int(width), int(height)
        self._style, self._nwc_style = loadstyle(style)
        # Standardize and check if language tag is a valid BCP 47 tag
        self._language = standardize_tag(language)
        self._locale = Locale.parse(self._language.replace("-", "_"))

        # For renaming regions to DW conventions
        self._translations = None

    def render(self, key: str, img_format: str, **kwargs):
        """Render file, and send to storage."""

        # Save plot in memory, to write it directly to storage
        auth_header = {
            "Authorization": f"Bearer {self.api_token}"
        }
        url = "https://api.datawrapper.de/v3/charts"

        # 1. create chart with metadata
        dw_data = self._prepare_dw_metadata(self.dw_data)
        # print(dw_data)
        r = requests.post(url, headers=auth_header, json=dw_data)
        try:
            r.raise_for_status()
        except Exception():
            msg = r.json()["message"]
            raise Exception(msg)

        self._dw_id = r.json()["id"]
        chart_id = self._dw_id

        url = f"https://api.datawrapper.de/v3/charts/{chart_id}"
        r = requests.get(url, headers=auth_header)

        # 2. add data
        # print("Add data")
        url = f"https://api.datawrapper.de/v3/charts/{chart_id}/data"
        csv_data = self._prepare_dw_chart_data()

        headers = deepcopy(auth_header)
        headers['content-type'] = 'text/csv; charset=UTF-8'
        r = requests.put(url, headers=headers, data=csv_data)
        r.raise_for_status()

        # 3. render (and store) chart
        # print("Store chart")
        url = f"https://api.datawrapper.de/v3/charts/{chart_id}/export/{img_format}"

        params = {
            "unit": "px",
            "mode": "rgb",
            "width": self._w,
            "plain": False,
            "zoom": 1,
        }
        # Datawrapper charts get auto height
        if self._h != 0:
            params["height"] = self._h
        # print(params)
        headers = deepcopy(auth_header)
        headers['accept'] = f'image/{img_format}'

        r = requests.post(url, json=params, headers=headers, stream=True)
        r.raise_for_status()
        buf = BytesIO(r.content)
        buf.seek(0)
        self._storage.save(key, buf, img_format)

    def render_all(self, key: str, **kwargs):
        """
        Render all available formats
        """

        for file_format in self.file_types:
            self.render(key, file_format)

        # In addition to regular format we store the Datawrapper chart
        # id in a basic text file to be able to to embeds.
        if self._dw_id is None:
            raise Exception("No Datawrapper id has been set. Has the chart been"
                            " created?")

        self._storage.save(key, self._dw_id, "dw")

    def _prepare_dw_metadata(self, dw_data):
        # 1. Common config
        dw_data["language"] = self._language

        # Follow DW convetions for language codes
        lang_code_translations = {
            "sv": "sv-SE",
            "en": "en-GB",
        }
        if dw_data["language"] in lang_code_translations:
            dw_data["language"] = lang_code_translations[dw_data["language"]]

        if "metadata" not in dw_data:
            dw_data["metadata"] = {}

        if "visualize" not in dw_data["metadata"]:
            dw_data["metadata"]["visualize"] = {}

        if self._title is not None:
            dw_data["title"] = self._title

        if self.caption is not None:
            if "describe" not in dw_data["metadata"]:
                dw_data["metadata"]["describe"] = {}

            dw_data["metadata"]["describe"]["source-name"] = self.caption

        if self.highlight:
            dw_data = self._apply_highlight(dw_data)

        # set number format
        if self.decimals is None:
            num_fmt = "0"
        else:
            num_fmt = "0.[{}]".format("0" * self.decimals)

        if self.units == "percent":
            # Values will also have to be multipled by 100 later
            num_fmt += "%"

        if 'y-grid-format' not in dw_data["metadata"]["visualize"]:
            dw_data["metadata"]["visualize"]['y-grid-format'] = num_fmt

        if "tooltip-number-format" not in dw_data["metadata"]["visualize"]:
            dw_data["metadata"]["visualize"]["tooltip-number-format"] = num_fmt

        # Line chart specific opts
        if dw_data["type"] == "d3-lines":
            if "labeling" not in dw_data["metadata"]["visualize"]:
                dw_data["metadata"]["visualize"]["labeling"] = "right"

        return dw_data

    def _prepare_dw_chart_data(self):
        """Transform chart data series to tabular shape and
        format as csv string for Datawrapper API.
        """
        if len(self.data) == 0:
            csv_str = ""

        # Data may be a list of dicts
        elif isinstance(self.data[0], dict):
            if self.dw_data["type"] == "d3-maps-choropleth":
                key_col = self.dw_data["metadata"]["axes"]["keys"]
                for row in self.data:
                    row[key_col] = self._translate_region(row[key_col])
            csv_str = _csv_str_from_list_of_dicts(self.data)

        # Or a structure that DataList can understand
        else:
            datalist = DataList()
            for series in self.data:
                datalist.append(series)

            rows = []
            if self.labels:
                rows.append([""] + self.labels)
            values = datalist.as_list_of_lists

            if self.units == "percent":
                # values have to be manually multipled by 100 for correct pct formatting
                values = [[v * 100 if v else None for v in series]
                          for series in values]

            cols = [datalist.x_points] + values
            # transpose
            value_rows = [x for x in map(list, zip(*cols))]
            rows += value_rows

            csv_str = _csv_str_from_list_of_rows(rows)

        return csv_str.encode("utf-8")

    def _apply_highlight(self, dw_data):
        """
        """
        chart_type = dw_data["type"]
        strong_color = rgb2hex(self._nwc_style["strong_color"])
        neutral_color = rgb2hex(self._nwc_style["neutral_color"])

        if chart_type in ["d3-lines"]:
            colors = {}
            for label in self.labels:
                if label == self.highlight:
                    colors[label] = strong_color
                    dw_data["metadata"]["visualize"]['highlighted-series'] = [label]
                else:
                    colors[label] = neutral_color

            dw_data["metadata"]["visualize"]["custom-colors"] = colors

            if len(self.labels) == 2 and self.highlight:
                dw_data["metadata"]["visualize"].update({
                    "fill-between": True,
                    'area-fill-color-between': '#cccccc',
                })

        elif chart_type in ["column-chart", "d3-bars"]:
            colors = {}

            for series in self.data:
                for d in series:
                    if isinstance(d, dict):
                        raise NotImplementedError("highlighting not implemented"
                                                  " for list of dicts")

                    ix = d[0]
                    # value = d[1]
                    if ix == self.highlight:
                        colors[ix] = strong_color
                    else:
                        colors[ix] = neutral_color

            dw_data["metadata"]["visualize"]["custom-colors"] = colors

        else:
            raise NotImplementedError(f"Unable to add highligt to {chart_type}")

        return dw_data

    def _translate_region(self, region):
        """Tries to translate a region name to DW convention.

        Lookup tables are defined in csv file.
        """
        if self._translations is None:
            _translations = {}
            file_path = os.path.join(HERE, 'translations', "datawrapper_regions.csv")
            with open(file_path) as f:
                for row in csv.DictReader(f, skipinitialspace=True):
                    _translations[row["newsworthy_id"]] = row["datawrapper_id"]
            self._translations = _translations

        try:
            return self._translations[region]
        except KeyError:
            return region


def _csv_str_from_list_of_rows(ll):
    """Make csv string from list of lists.

    :param data: list of lists (representing rows and cells)
    """
    csv_str = StringIO()
    writer = csv.writer(csv_str)
    writer.writerows(ll)
    return csv_str.getvalue()


def _csv_str_from_list_of_dicts(list_of_dicts):
    csv_str = StringIO()
    cols = set().union(*(d.keys() for d in list_of_dicts))
    writer = csv.DictWriter(csv_str, fieldnames=cols)
    writer.writeheader()
    writer.writerows(list_of_dicts)
    return csv_str.getvalue()
