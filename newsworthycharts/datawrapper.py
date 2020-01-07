from babel import Locale
import os
from langcodes import standardize_tag
import requests
from copy import deepcopy
from io import BytesIO, StringIO
import csv

from .storage import Storage, LocalStorage
from .chart import Chart
from .lib.utils import loadstyle
from .lib.formatter import Formatter
from .lib.datalist import DataList

class DatawrapperChart(Chart):
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

        self.dw_data = {}


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
        dw_data = self._prepare_dw_data(self.dw_data)
        print(dw_data)
        r = requests.post(url, headers=auth_header, json=dw_data)
        r.raise_for_status()

        chart_id = r.json()["id"]

        url = f"https://api.datawrapper.de/v3/charts/{chart_id}"
        r = requests.get(url, headers=auth_header)
        print(r.json())

        # 2. add data
        print("Add data")
        url = f"https://api.datawrapper.de/v3/charts/{chart_id}/data"
        data = []
        if self.labels:
            data.append([""] + self.labels)
        cols = [self.data.x_points] + self.data.as_list_of_lists
        # transpose
        rows = [x for x in map(list, zip(*cols))]
        data += rows

        csv_data = _to_csv_str(data)

        headers = deepcopy(auth_header)
        headers['content-type'] = 'text/csv'
        r = requests.put(url, headers=headers, data=csv_data)
        r.raise_for_status()


        # 3. render (and store) chart

        print("Store chart")
        url = f"https://api.datawrapper.de/v3/charts/{chart_id}/export/{img_format}"

        querystring = {
            "unit": "px",
            "mode": "rgb",
            "width": self._w,
            "plain": False,
            "scale": 1,
        }
        if self._h != 0:
            querystring["height"] = self._h
        print(querystring)
        headers = deepcopy(auth_header)
        headers['accept'] = f'image/{img_format}'

        r = requests.get(url, params=querystring, headers=headers, stream=True)
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

    def _prepare_dw_data(self, dw_data):
        # 1. Common config
        dw_data["utf8"] = True
        dw_data["language"] = self._language

        if self._title is not None:
            dw_data["title"] = self._title

        if self.caption is not None:
            dw_data["metadata"]["describe"]["source-name"] = self.caption

        if self.highlight:
            dw_data = self._apply_highlight(dw_data)

        return dw_data

    def _apply_highlight(self, dw_data):
        chart_type = dw_data["type"]
        if chart_type == "d3-lines":
            colors = {}
            for label in self.labels:
                if label == self.highlight:
                    colors[label] = "#ff0000" # self._style["strong_color"]
                else:
                    colors[label] = "#333333"#self._style["neutral_color"]
                    # TODO: defaultdict solution would be prettier
                    try:
                        dw_data["metadata"]["visualize"]["custom-colors"] = colors
                    except KeyError:
                        dw_data["metadata"]["visualize"] = {
                            "custom-colors": colors
                        }
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
