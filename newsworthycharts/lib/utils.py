""" Various utility methods """
import os
from datetime import datetime
import yaml
from matplotlib import rc_file, rcParams
from matplotlib.colors import to_rgba
from .colors import POSITIVE, NEGATIVE, FILL_BETWEEN, WARM, COLD, QUALITATIVE


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
    style["title_font"] = [x.strip()
                           for x in rc_params_newsworthy["title_font"]
                           .split(",")]
    color = rc_params_newsworthy.get("neutral_color",
                                     rcParams["figure.edgecolor"])
    strong_color = rc_params_newsworthy.get("strong_color", color)
    positive_color = rc_params_newsworthy.get("positive_color", POSITIVE)
    negative_color = rc_params_newsworthy.get("negative_color", NEGATIVE)
    warm_color = rc_params_newsworthy.get("warm_color", WARM)
    cold_color = rc_params_newsworthy.get("cold_color", COLD)
    fill_between_color = rc_params_newsworthy.get("fill_between_color", FILL_BETWEEN)
    fill_between_alpha = rc_params_newsworthy.get("fill_between_alpha", 0.5)
    style["neutral_color"] = to_rgba("#" + str(color), 1)
    style["strong_color"] = to_rgba("#" + str(strong_color), 1)
    style["positive_color"] = to_rgba("#" + positive_color, 1)
    style["negative_color"] = to_rgba("#" + negative_color, 1)
    style["warm_color"] = to_rgba("#" + warm_color, 1)
    style["cold_color"] = to_rgba("#" + cold_color, 1)
    style["fill_between_color"] = to_rgba("#" + str(fill_between_color), 1)
    style["fill_between_alpha"] = float(fill_between_alpha)
    # TODO: Make it possible to define in in style file
    style["qualitative_colors"] = [to_rgba("#" + c, 1) for c in QUALITATIVE]
    if "logo" in rc_params_newsworthy:
        style["logo"] = rc_params_newsworthy["logo"]

    return style


def to_float(val):
    """Convert string to float, but also handles None and 'null'."""
    if val is None:
        return None
    if str(val) == "null":
        return None
    return float(val)


def to_date(val):
    """Convert date string to datetime date."""
    return datetime.strptime(val, "%Y-%m-%d")
