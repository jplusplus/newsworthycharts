""" Various utility methods """
from matplotlib import rc_file, rcParams
from matplotlib.colors import to_rgba
from datetime import datetime
import os
import yaml

HERE = os.path.dirname(__file__)


class StyleNotFoundError(FileNotFoundError):
    pass


def loadstyle(style_name):
    """ Load a custom style file, adding both rcParams and custom params.
    Writing a proper parser for these settings is in the Matplotlib backlog,
    so let's keep calm and avoid inventing their wheel.
    """

    style = {}
    style_file = os.path.join(HERE, 'rc', style_name)
    try:
        # Check rc directory for built in styles first
        rc_file(style_file)
    except FileNotFoundError as e:
        # Check current working dir or path
        style_file = style_name
        try:
            rc_file(style_file)
        except FileNotFoundError as e:
            raise StyleNotFoundError("No such style file found")
    style = rcParams.copy()

    # The style files may also contain an extra section with typography
    # for titles and captions (these can only be separately styled in code,
    # as of Matplotlib 2.2)
    # This is a hack, but it's nice to have all styling in one file
    # The extra styling is prefixed with `#!`
    with open(style_file, 'r') as f:
        doc = f.readlines()
        rcParamsNewsworthy = "\n".join([d[2:]
                                       for d in doc if d.startswith("#!")])
    rcParamsNewsworthy = yaml.load(rcParamsNewsworthy)
    style["title_font"] = [x.strip()
                           for x in rcParamsNewsworthy["title_font"]
                           .split(",")]
    color = rcParamsNewsworthy.get("neutral_color",
                                   rcParams["figure.edgecolor"])
    strong_color = rcParamsNewsworthy.get("strong_color", color)
    fill_between_color = rcParamsNewsworthy.get("fill_between_color", "F7F4F4")
    fill_between_alpha = rcParamsNewsworthy.get("fill_between_alpha", 0.5)
    style["neutral_color"] = to_rgba("#" + str(color), 1)
    style["strong_color"] = to_rgba("#" + str(strong_color), 1)
    style["fill_between_color"] = to_rgba("#" + str(fill_between_color), 1)
    style["fill_between_alpha"] = float(fill_between_alpha)
    if "logo" in rcParamsNewsworthy:
        style["logo"] = rcParamsNewsworthy["logo"]

    return style


def rpad(list_, item, length):
    """
     Right pad a list to a certain length, using `item`
    """
    if list_ is None:
        list_ = []
    return list_ + [item for i in range(max(0, length-len(list_)))]


def to_float(s):
    """Convert string to float, but also handles None and 'null'."""
    if s is None:
        return None
    if str(s) == "null":
        return
    return float(s)


def to_date(s):
    """Convert date string to datetime date."""
    return datetime.strptime(s, "%Y-%m-%d")
