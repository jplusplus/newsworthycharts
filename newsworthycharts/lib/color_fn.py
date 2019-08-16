"""Functions for deteriming colors accoriding to some rule.
"""

def positive_negative(value):
    """Return positive/negative color based on a value being
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
