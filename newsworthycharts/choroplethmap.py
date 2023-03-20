"""
Simple choropleths for common administrative areas
"""
from .chart import Chart
from .lib.geography import haversine
from .translations.regions import NW_MUNI_TO_CLDR
from fiona.errors import DriverError
from shapely.geometry.multipolygon import MultiPolygon
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

REGION_TRANSLATIONS = {
    "se-7": NW_MUNI_TO_CLDR,
    "se-7-inset": NW_MUNI_TO_CLDR,
}


class ChoroplethMap(Chart):
    """Plot a dataset on a coropleth map

    Data should be an iterables of (region, value) tuples, eg:
    `[("SE-8", 2), ("SE-9", 2.3)]`
    Newsworthy region names are also supported:
    `[("Stockholms kommun", 2), ("Solna kommun", 2.3)]`
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
        self.missing_label = None
        self.df = None

    def _normalize_region_code(self, code):
        code = code.upper().replace("_", "-")
        # Apply translation, if we find and applicable one
        region_translation = REGION_TRANSLATIONS.get(self.base_map, {})
        region_translation = {k.upper(): v for k, v in region_translation.items()}
        code = region_translation.get(code, code)
        return code

    def _get_height(self, w):

        (minx, miny, maxx, maxy) = self.df.total_bounds

        # Calculate height from bbox, but limiting aspect to at most 1:1
        if self.df.crs.is_projected:
            dist_w = maxx - minx
            dist_h = maxy - miny
        else:
            dist_w = haversine(minx, maxy, maxx, maxy)
            dist_h = haversine(minx, miny, minx, maxy)
        dist_ratio = dist_h / dist_w
        height = int(float(w) * dist_ratio)
        if height > w:
            height = w
        return height

    def parse_basemap(self):
        # FIXME: Make a basemap setter that handles parsing
        _bm = self.base_map  # ["se-7-inset", "se-7", "se-4", "se01-7", ...]
        base_map, subdivisions, *opts = _bm.split("-")
        # Save save precious AWS Lambda bytes by reusing geodata
        # se|03-7 filter se by prefix 03
        _ = base_map.split("|")
        subset = None
        if len(_) > 1:
            [base_map, subset] = _

        if not self.df:
            __dir = pathlib.Path(__file__).parent.resolve()
            try:
                self.df = gpd.read_file(f"{__dir}/maps/{base_map}-{subdivisions}.gpkg")
            except DriverError:
                raise ValueError(
                    f"No such basemap: {_bm} (parsed as base: {base_map}, subdivisions: {subdivisions})"
                )
        return base_map, subdivisions, subset, *opts

    def _add_data(self):

        base_map, subdivisions, subset, *opts = self.parse_basemap()
        df = self.df

        if "inset" in opts:
            inset = "-".join([base_map, subdivisions])
            self.insets = INSETS[inset]
        else:
            self.insets = []

        if len(self.data) > 1:
            raise ValueError("Choropleth maps can only display one data series at a time")

        series = self.data[0]
        series = [(self._normalize_region_code(x[0]), x[1]) for x in series]

        if subset:
            def norm(id_):
                # This is a hack to allow `se|03-7` rather than `se|'SE-03'-7`
                id_ = id_.replace("-", "").replace("_", "").lower()
                if id_.startswith(base_map):
                    id_ = id_[len(base_map):]
                return id_
            df["_norm_id"] = df["id"].apply(norm)
            df = df[df["_norm_id"].str.startswith(subset)].copy()

        available_codes = df["id"].to_list()
        if not all([x[0] in available_codes for x in series]):
            invalid_codes = [x[0] for x in series if not x[0] in available_codes]
            raise ValueError(f"Invalid region code(s): {', '.join(invalid_codes)}")
        datamap = {x[0]: x[1] for x in series}
        df["data"] = df["id"].map(datamap)  # .astype("category")

        if self.categorical:
            # We'll categorize manually further down the line,
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

            # df["data"] = pd.merge(_has_value, df, on="id", how="right")["cats"]
            _dict = _has_value[["id", "cats"]].set_index("id").to_dict()
            df["data"] = df["id"].map(_dict["cats"])

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
        # This should be adjusted per basemap
        label_kwargs = {
            "bbox_to_anchor": (0.92, 0.95),
            "loc": "upper left",
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
                **label_kwargs
            )

        fig = df.plot(ax=self.ax, **args)
        # Add outer edge
        unary = df.unary_union
        if unary.geom_type == "Polygon":
            # We don't know in advance if unary_union will produce a polugon or a multipolygon
            unary = MultiPolygon([unary])
        for uu in unary.geoms:
            gpd.GeoSeries(uu).plot(
                ax=self.ax,
                edgecolor="lightgrey",
                linewidth=0.2,
                facecolor="none",
            )
        self.ax.axis("off")

        # Format numbers in legend
        if not self.categorical:
            leg = fig.get_legend()
            fmt = self._get_value_axis_formatter()
            remove_last = False
            for lbl in leg.get_texts():
                val = lbl.get_text()
                if val == "NaN":  # as returned by mapclassify
                    if self.missing_label is not None:
                        val = self.missing_label
                    else:
                        remove_last = True
                        val = ""
                else:
                    val = float(val)
                    val = fmt(val)
                lbl.set_text(val)
            if remove_last:
                del leg.legend_handles[-1]
                texts = [lbl.get_text() for lbl in leg.get_texts()]
                fig.legend(handles=leg.legend_handles, labels=texts, **label_kwargs)

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
            gpd.GeoSeries(_df.unary_union).plot(
                ax=axin,
                edgecolor="lightgrey",
                linewidth=0.3,
                facecolor="none",
            )
            axin.axis('off')
            _df.plot(
                ax=axin,
                **args,
            )
            r, (a, b, c, d) = self.ax.indicate_inset_zoom(axin)
            for _line in [a, b, c, d]:
                _line.set_visible(False)
