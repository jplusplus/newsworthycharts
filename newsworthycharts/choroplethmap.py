"""
Simple choropleths for common administrative areas
"""
from .map import Map
from shapely.geometry.multipolygon import MultiPolygon
import geopandas as gpd
import numpy as np
import pandas as pd
import mapclassify


class ChoroplethMap(Map):
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

    def _add_data(self):

        df = self._prepare_map_data()

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
        # unary_union does not work with Multipolygons
        mp = MultiPolygon([g for g in df.explode(index_parts=True).geometry])
        gpd.GeoSeries(mp.boundary).plot(
            ax=self.ax,
            edgecolor="lightgrey",
            linewidth=0.2,
            color="none",
        )
        """
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
        """
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
