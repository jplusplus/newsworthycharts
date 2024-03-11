"""
Simple bubble map for common administrative areas
"""
from .map import Map
from shapely.geometry.multipolygon import MultiPolygon
import geopandas as gpd


class BubbleMap(Map):
    """Plot a dataset on a bubble map

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
        super(BubbleMap, self).__init__(*args, **kwargs)
        self.bubble_size = kwargs.get("bubble_size", 1)

    def _add_data(self):

        df = self._prepare_map_data()

        if self.colors:
            color = self.colors[0]
        else:
            color = self._nwc_style["strong_color"]

        args = {
            "categorical": True,
            "legend": True,  # bug in geopandas, fixed in master but not released
            "legend_kwds": {
                "loc": "upper left",
                "bbox_to_anchor": (1.05, 1.0),
            },
            "edgecolor": "white",
            "linewidth": 0.2,
            "color": "gainsboro"
        }

        df.plot(ax=self.ax, **args)

        # Add outer edge
        # unary_union does not work with Multipolygons, so explode polygons, and use boundary
        mp = MultiPolygon([g for g in df.explode(index_parts=True).geometry])
        gpd.GeoSeries(mp.boundary).plot(
            ax=self.ax,
            edgecolor="lightgrey",
            linewidth=0.2,
            color="none",
        )

        # Plot bubbles
        centroids = df.copy()
        centroids.geometry = df.representative_point()
        bounds = df.bounds
        # Let largest circle be the size of the region
        bounds["width"] = bounds["maxx"] - bounds["minx"]
        factor = bounds["width"].max() / 2

        # pixel conversion for markersize
        ax_width = self.ax.get_xlim()[1] - self.ax.get_xlim()[0]
        unit_per_pixel = ax_width / self._w

        centroids["size"] = \
            (centroids["data"] / centroids["data"].max()) \
            * factor / unit_per_pixel * self.bubble_size
        centroids.plot(markersize="size", ax=self.ax, alpha=0.5, facecolor=color)

        self.ax.axis("off")

        for inset in self.insets:
            raise NotImplementedError("Bubble maps do not yet support insets")
