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
from .lib.formatter import Formatter
from .lib.datalist import DataList

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
        self.data = DataList()  # A list of datasets
        self.labels = []  # Optionally one label for each dataset
        self.annotations = []  # Manually added annotations
        self.caption = None
        self.highlight = None
        self.decimals = None

        self.dw_data = {}
        self._dw_id = None # Datawrapper chart id


        # P R I V A T E   P R O P E R T I E S
        # Properties managed through getters/setters
        self._title = None
        self._units = "count"

        # Calculated properties
        self._storage = storage
        self._w, self._h = int(width), int(height)
        self._style = loadstyle(style)
        # Standardize and check if language tag is a valid BCP 47 tag
        self._language = standardize_tag(language)
        self._locale = Locale.parse(self._language.replace("-", "_"))



    def render(self, key: str, img_format: str):
        """Render file, and send to storage."""

        # Save plot in memory, to write it directly to storage
        auth_header = {
            "Authorization": f"Bearer {self.api_token}"
        }
        url = "https://api.datawrapper.de/v3/charts"

        # 1. create chart with metadata
        dw_data = self._prepare_dw_metadata(self.dw_data)
        #print(dw_data)
        r = requests.post(url, headers=auth_header, json=dw_data)
        r.raise_for_status()

        self._dw_id = r.json()["id"]
        chart_id = self._dw_id

        url = f"https://api.datawrapper.de/v3/charts/{chart_id}"
        r = requests.get(url, headers=auth_header)

        # 2. add data
        #print("Add data")
        url = f"https://api.datawrapper.de/v3/charts/{chart_id}/data"
        csv_data = self._prepare_dw_chart_data()

        headers = deepcopy(auth_header)
        headers['content-type'] = 'text/csv; charset=UTF-8'
        r = requests.put(url, headers=headers, data=csv_data)
        r.raise_for_status()


        # 3. render (and store) chart
        #print("Store chart")
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
        #print(params)
        headers = deepcopy(auth_header)
        headers['accept'] = f'image/{img_format}'

        r = requests.post(url, json=params, headers=headers, stream=True)
        r.raise_for_status()
        buf = BytesIO(r.content)
        buf.seek(0)
        self._storage.save(key, buf, img_format)


    def render_all(self, key: str):
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
        dw_data["utf8"] = True
        dw_data["language"] = self._language

        if not "visualize" in dw_data["metadata"]:
            dw_data["metadata"]["visualize"] = {}

        if self._title is not None:
            dw_data["title"] = self._title

        if self.caption is not None:
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

        # 2. Line chart specific opts
        if dw_data["type"] == "d3-lines":
            if "labeling" not in dw_data["metadata"]["visualize"]:
                dw_data["metadata"]["visualize"]["labeling"] = "right"

        return dw_data

    def _prepare_dw_chart_data(self):
        """Transform chart data series to tabular shape and
        format as csv string for Datawrapper API.
        """
        data = []
        if self.labels:
            data.append([""] + self.labels)
        values = self.data.as_list_of_lists

        if self.units == "percent":
            # values have to be manually multipled by 100 for correct pct formatting
            values = [[v * 100 if v else None for v in series]
                      for series in values]

        cols = [self.data.x_points] + values
        # transpose
        rows = [x for x in map(list, zip(*cols))]
        data += rows

        csv_str = _to_csv_str(data)

        return csv_str.encode("utf-8")


    def _apply_highlight(self, dw_data):
        """
        """
        chart_type = dw_data["type"]
        strong_color = rgb2hex(self._style["strong_color"])
        neutral_color = rgb2hex(self._style["neutral_color"])

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
                for ix, value, _ in series:
                    if ix == self.highlight:
                        colors[ix] = strong_color
                    else:
                        colors[ix] = neutral_color

            dw_data["metadata"]["visualize"]["custom-colors"] = colors

        else:
            raise NotImplementedError(f"Unable to add highligt to {chart_type}")

        return dw_data

def _to_csv_str(ll):
    """Make csv string from list of lists.

    :param data: list of lists (representing rows and cells)
    """
    csv_str = StringIO()
    writer = csv.writer(csv_str)
    writer.writerows(ll)
    return csv_str.getvalue()
