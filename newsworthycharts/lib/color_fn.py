""" Functions for determining colors accoriding to some rule.
"""


def color_fn(func):
    """ Wrapper that validates respones
    """
    def validate_response(*args, **kwargs):
        """ Check that returned value is valid
        """
        resp = func(*args, **kwargs)
        named_colors = ["neutral", "strong", "positive", "negative", "warm", "cold"]
        if resp not in named_colors:
            # TODO: Also allow valid HEX colors
            raise Exception("{} is not a valid color name".format(resp))
        return resp

    return validate_response


@color_fn
def positive_negative(value, baseline=0):
    """ Return positive/negative color based on a value being
    above/below 0.
    """
    if value is None:
        color_name = "neutral"
    elif value < 0:
        color_name = "negative"
    elif value > 0:
        color_name = "positive"
    else:
        color_name = "neutral"

    return color_name


@color_fn
def warm_cold(value, baseline=0):
    """ Return warm/cold color based on a value being
    above/below a baseline.
    """
    if value is None:
        color_name = "neutral"
    elif value < 0:
        color_name = "cold"
    elif value > 0:
        color_name = "warm"
    else:
        color_name = "neutral"

    return color_name
