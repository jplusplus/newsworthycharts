""" Various utility methods """
from matplotlib import rc_file, rcParams
from matplotlib.colors import to_rgba
import os
import yaml

HERE = os.path.dirname(__file__)


class StyleNotFoundError(FileNotFoundError):
    pass


def loadstyle(style_name):
    """ Load a custom style file, adding both rcParams and custom params """

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
    style["neutral_color"] = to_rgba("#" + str(color), 1)
    style["strong_color"] = to_rgba("#" + str(strong_color), 1)

    return style
