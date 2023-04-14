""" Various utility methods """
import os
from datetime import datetime
import numpy as np
import yaml
from matplotlib import rc_file, rcParams
from matplotlib.colors import to_rgba, cnames, to_rgb
import matplotlib.patheffects as pe
import colorsys

from .colors import BLACK, DARK_GRAY, LIGHT_GRAY, POSITIVE, NEGATIVE, FILL_BETWEEN, WARM, COLD, QUALITATIVE


HERE = os.path.dirname(__file__)


class StyleNotFoundError(FileNotFoundError):
    """ No style file matching the given name could be found or loaded """
    pass


def loadstyle(style_name):
    """ Load a custom style file, adding both rcParams and custom params.
    Writing a proper parser for these settings is in the Matplotlib backlog,
    so let's keep calm and avoid inventing their wheel.
    """

    style = {}
    nwc_styles = {}  # for backwards compatibility
    style_file = os.path.join(HERE, '..', 'rc', style_name)
    try:
        # Check rc directory for built in styles first
        rc_file(style_file)
    except FileNotFoundError:
        # Check current working dir or path
        style_file = style_name
        try:
            rc_file(style_file)
        except FileNotFoundError as err:
            raise StyleNotFoundError(f"No such style file found: {err}")
    style = rcParams.copy()

    # The style files may also contain an extra section with typography
    # for titles and captions (these can only be separately styled in code,
    # as of Matplotlib 2.2)
    # This is a hack, but it's nice to have all styling in one file
    # The extra styling is prefixed with `#!`
    with open(style_file, 'r') as file_:
        doc = file_.readlines()
        rc_params_newsworthy = "\n".join([d[2:]
                                          for d in doc if d.startswith("#!")])
    rc_params_newsworthy = yaml.safe_load(rc_params_newsworthy)
    ###
    # Typography
    ###
    if "title_font" in rc_params_newsworthy:
        nwc_styles["title_font"] = [
            x.strip() for x in rc_params_newsworthy["title_font"].split(",")
        ]
    else:
        nwc_styles["title_font"] = style["font.family"]

    # define as pt or reltive ("smaller")
    nwc_styles["subtitle.fontsize"] = rc_params_newsworthy.get(
        "subtitle.fontsize",
        None,
    )

    # make annotation same font size as ticks by default
    tick_font_size = style.get('xtick.labelsize', "smaller")
    nwc_styles["annotation.fontsize"] = rc_params_newsworthy.get(
        "annotation.fontsize",
        tick_font_size,
    )
    nwc_styles["note.fontsize"] = rc_params_newsworthy.get(
        "note.fontsize",
        "smaller",
    )
    nwc_styles["caption.fontsize"] = rc_params_newsworthy.get(
        "caption.fontsize",
        "smaller",
    )

    color = rc_params_newsworthy.get("neutral_color",
                                     rcParams["figure.edgecolor"])
    black_color = rc_params_newsworthy.get("black_color", BLACK)
    dark_gray_color = rc_params_newsworthy.get("dark_gray_color", DARK_GRAY)
    light_gray_color = rc_params_newsworthy.get("light_gray_color", LIGHT_GRAY)
    strong_color = rc_params_newsworthy.get("strong_color", color)
    positive_color = rc_params_newsworthy.get("positive_color", POSITIVE)
    negative_color = rc_params_newsworthy.get("negative_color", NEGATIVE)
    warm_color = rc_params_newsworthy.get("warm_color", WARM)
    cold_color = rc_params_newsworthy.get("cold_color", COLD)
    fill_between_color = rc_params_newsworthy.get("fill_between_color", FILL_BETWEEN)
    fill_between_alpha = rc_params_newsworthy.get("fill_between_alpha", 0.5)
    nwc_styles["black_color"] = to_rgba("#" + str(black_color), 1)
    nwc_styles["dark_gray_color"] = to_rgba("#" + str(dark_gray_color), 1)
    nwc_styles["light_gray_color"] = to_rgba("#" + str(light_gray_color), 1)
    nwc_styles["neutral_color"] = to_rgba("#" + str(color), 1)
    nwc_styles["strong_color"] = to_rgba("#" + str(strong_color), 1)
    nwc_styles["positive_color"] = to_rgba("#" + positive_color, 1)
    nwc_styles["negative_color"] = to_rgba("#" + negative_color, 1)
    nwc_styles["warm_color"] = to_rgba("#" + warm_color, 1)
    nwc_styles["cold_color"] = to_rgba("#" + cold_color, 1)
    nwc_styles["fill_between_color"] = to_rgba("#" + str(fill_between_color), 1)
    nwc_styles["fill_between_alpha"] = float(fill_between_alpha)

    if "qualitative_colors" in rc_params_newsworthy:
        nwc_styles["qualitative_colors"] = [
            to_rgba("#" + c.strip(), 1)
            for c in rc_params_newsworthy["qualitative_colors"].split(",")
        ]

    else:
        nwc_styles["qualitative_colors"] = [to_rgba("#" + c, 1) for c in QUALITATIVE]
    if "logo" in rc_params_newsworthy:
        nwc_styles["logo"] = rc_params_newsworthy["logo"]

    return style, nwc_styles


def to_float(val):
    """Convert string to float, but also handles None and 'null'."""
    if val is None:
        return None
    if str(val) == "null":
        return None
    return float(val)


def to_date(val):
    """Convert date string to datetime date.

    Integers are interpreted as years.
    """
    if np.issubdtype(type(val), np.integer) and val < 3000:
        return datetime(val, 1, 1)
    try:
        return datetime.strptime(val, "%Y-%m-%d")

    except ValueError:
        return datetime.strptime(val, "%Y")
    except Exception:
        raise ValueError(f"Unable to parse date from {val}")


def adjust_lightness(color, amount=0.5):
    """Lighten/darken color.
    """
    try:
        c = cnames[color]
    except Exception:
        c = color
    c = colorsys.rgb_to_hls(*to_rgb(c))
    return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])


def outline(color="white", linewidth=3, **kwargs):
    """Short-cut for generering an outline with `path_effects`
    """
    return [pe.withStroke(linewidth=linewidth, foreground=color, **kwargs)]


def guess_date_interval(data):
    """Return a probable interval, e.g. "montly", given current data."""
    interval = "yearly"
    for serie in data:
        dates = [to_date(x[0]) for x in serie]
        years = [x.year for x in dates]
        months = [x.month for x in dates]
        yearmonths = [x.strftime("%Y-%m") for x in dates]
        weeks = [str(x.year) + str(x.isocalendar()[1]) for x in dates]
        if len(years) > len(set(years)):
            # there are years with more than one point
            unique_months = sorted(list(set(months)))
            if len(unique_months) == 4 \
                    and unique_months[0] + 3 == unique_months[1] \
                    and unique_months[1] + 3 == unique_months[2] \
                    and unique_months[2] + 3 == unique_months[3]:
                # all in all four months, and they are non-conscutive
                interval = "quarterly"
            else:
                interval = "monthly"
                if len(yearmonths) > len(set(yearmonths)):
                    interval = "weekly"
                if len(weeks) > len(set(weeks)):
                    interval = "daily"
    return interval
