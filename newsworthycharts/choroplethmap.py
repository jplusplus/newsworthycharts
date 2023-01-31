"""
Simple choropleths for common administrative areas
"""
from .chart import Chart
import geopandas as gpd
import numpy as np
import pandas as pd
import mapclassify
import pathlib


INSETS = {
    "se-7": [
        {
            "id": "Stockholms län",
            "prefix": "SE-01",
            "axes": [0.71, 0.30, 0.4, 0.35],
        },
        {
            "id": "Storgöteborg",
            "list": [
                "SE-1402",
                "SE-1407",
                "SE-1481",
                "SE-1482",  # Kungälv
                "SE-1480",
                "SE-1415",  # Stenungsund
                "SE-1419",  # Tjörn
                "SE-1401",  # Härryda
                "SE-1441",  # Lerum
                "SE-1440",  # Ale
                "SE-1462",  # L:a Edet
                "SE-1485",  # Uddevalla
                "SE-1421",  # Orust
                "SE-1484",  # Lysekil
                "SE-1427",  # Sotenäs
            ],
            "axes": [-0.28, 0.14, 0.3, 0.4],
        },
        {
            "id": "Malmöhus",
            "list": [
                "SE-1260",
                "SE-1233",
                "SE-1287",
                "SE-1263",
                "SE-1214",
                "SE-1230",
                "SE-1264",
                "SE-1265",
                "SE-1280",
                "SE-1281",
                "SE-1262",
                "SE-1282",
                "SE-1261",
                "SE-1267",
                "SE-1266",
                "SE-1283",
                "SE-1285",
                "SE-1231",
                "SE-1286",
            ],
            "axes": [-0.13, -0.13, 0.3, 0.3],
        },
    ],
}


class ChoroplethMap(Chart):
    """Plot a dataset on a coropleth map

    Data should be an iterables of (region, value) tuples, eg:
    `[("SE-8", 2), ("SE-9", 2.3)]`
    Note that unlike many other chart types, this one only allows
    a single dataset to be plotted, and the data is hence provided
    as a single iterable, rather than a list of iterables.
    """

    _uses_categorical_data = True

    def __init__(self, *args, **kwargs):
        super(ChoroplethMap, self).__init__(*args, **kwargs)
        self.bins = kwargs.get("bins", 9)
        self.binning_method = kwargs.get("binning_method", "natural_breaks")
        self.color_ramp = kwargs.get("color_ramp", "YlOrRd")
        self.categorical = kwargs.get("categorical", False)
        self.base_map = None

    def _add_data(self):
        _bm = self.base_map  # ["se-7-inset", "se-7", "se-4", "se01-7", ...]
        base_map, subdivisions, *opts = _bm.split("-")
        if "inset" in opts:
            inset = "-".join([base_map, subdivisions])
            self.insets = INSETS[inset]
        else:
            self.insets = []

        series = self.data[0]
        datamap = {x[0]: x[1] for x in series}
        __dir = pathlib.Path(__file__).parent.resolve()
        df = gpd.read_file(f"{__dir}/maps/{base_map}-{subdivisions}.gpkg")
        df["data"] = df["id"].map(datamap)  # .astype("category")

        if self.categorical:
            # Custom colors
            df["data"] = pd.Categorical(
                df["data"],
                ordered=True,
            )
        else:
            _has_value = df[~df["data"].isna()].copy()
            binning = mapclassify.classify(
                np.asarray(_has_value["data"]),  # .astype("category")
                self.binning_method,
                k=self.bins
            )
            values = pd.Categorical.from_codes(
                binning.yb,
                categories=binning.bins,
                ordered=True
            )
            _has_value["cats"] = values
            df["data"] = pd.merge(_has_value, df, on="id", how="right")["cats"]

        args = {
            "column": "data",
            "categorical": True,
            "cmap": self.color_ramp,
            "legend": True,  # bug in geopandas, fixed in master but not released
            "legend_kwds": {
                "loc": "upper left",
                "bbox_to_anchor": (1.05, 1.0),
            },
            "edgecolor": "white",
            "linewidth": 0.2,
            "missing_kwds": {
                "color": "lightgrey",
            },
        }
        if not self.categorical:
            args["cmap"] = self.color_ramp
        df.plot(ax=self.ax, **args)
        self.ax.axis("off")

        for inset in self.insets:
            axin = self.ax.inset_axes(inset["axes"])
            axin.axis('off')
            if "prefix" in inset:
                _df = df[df["id"].str.startswith(inset["prefix"])].copy()
            else:
                _df = df[df["id"].isin(inset["list"])].copy()
            _df.plot(
                ax=axin,
                column="data",
                categorical=True,
                # cmap=self.color_ramp,
                edgecolor='white',
                linewidth=0.2,
                missing_kwds={
                    "color": "lightgrey",
                },
            )
            r, (a, b, c, d) = self.ax.indicate_inset_zoom(axin)
            for _line in [a, b, c, d]:
                _line.set_visible(False)
