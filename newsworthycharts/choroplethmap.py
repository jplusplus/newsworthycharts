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
        self.colors = kwargs.get("colors", None)
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
            # We'll categorize manually below,
            # to easier implement custom coloring
            pass
            # df["data"] = pd.Categorical(
            #     df["data"],
            #     ordered=True,
            # )
        else:
            # mapclassify doesn't work well with nan values,
            # but we to keep them for plotting, hence
            # this hack with cutting out nan's and re-pasting them below
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
            "categorical": True,
            "legend": True,  # bug in geopandas, fixed in master but not released
            "legend_kwds": {
                "loc": "upper left",
                "bbox_to_anchor": (1.05, 1.0),
            },
            "edgecolor": "white",
            "linewidth": 0.2,
            "missing_kwds": {
                "color": "gainsboro",
            },
        }
        if not self.categorical:
            args["cmap"] = self.color_ramp
            args["column"] = "data"
        if self.categorical:
            cat = df[~df["data"].isna()]["data"].unique()
            args["categories"] = cat
            if self.colors:
                color_map = self.colors
            else:
                color_map = {}
                for idx, cat in enumerate(cat):
                    color_map[cat] = self._nwc_style["qualitative_colors"][idx]
            df["color"] = df["data"].map(color_map)
            df["color"] = df["color"].fillna("gainsboro")
            args["color"] = df["color"]

            # Geopandas does not handle legend if color keyword is used
            # We need to add it ourselves
            import matplotlib.patches as mpatches
            patches = []
            for label, color in color_map.items():
                # A bit of an hack:
                # Check if this corresponds to one of our predefined
                # color names:
                if f"{color}_color" in self._nwc_style:
                    color = self._nwc_style[f"{color}_color"]
                patch = mpatches.Patch(color=color, label=label)
                patches.append(patch)
            self.ax.legend(
                handles=patches,
                # This have to be adjusted per basemap
                bbox_to_anchor=(1, 0.95),
                loc="upper left",
            )

        df.plot(ax=self.ax, **args)
        self.ax.axis("off")

        for inset in self.insets:
            if "prefix" in inset:
                _df = df[df["id"].str.startswith(inset["prefix"])].copy()
            else:
                _df = df[df["id"].isin(inset["list"])].copy()
            if _df["data"].isnull().all():
                # Skip if no data
                continue
            if self.categorical:
                # We need a series matching the filtered data
                args["color"] = _df["color"]
            args["legend"] = False
            axin = self.ax.inset_axes(inset["axes"])
            axin.axis('off')
            _df.plot(
                ax=axin,
                **args,
            )
            r, (a, b, c, d) = self.ax.indicate_inset_zoom(axin)
            for _line in [a, b, c, d]:
                _line.set_visible(False)
