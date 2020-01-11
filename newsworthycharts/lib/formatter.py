"""Module for doing (very) simple i18n work."""
from babel.numbers import format_decimal, format_percent, Locale
from babel.units import format_unit
from decimal import Decimal


class Formatter(object):
    """A formatter for a specific language and locale.

    Contains some methods for number and text formatting.
    Heavier i18n work should be before involving newsworthycharts.
    Usage:

     >>> fmt = Formatter("sv-SE")
     >>> fmt.percent(0.14)
     "14 %"
    """

    def __init__(self, lang, decimals: int=None, scale: str="celcius"):
        """Create formatter for specific locale."""
        self.l = Locale.parse(lang.replace("-", "_"))  # NOQA
        self.language = self.l.language
        self.decimals = decimals
        self.scale = scale

    def __repr__(self):
        return "Formatter: " + repr(self.l)

    def __str__(self):
        return self.l.get_display_name()

    def percent(self, x, *args, **kwargs):

        if self.decimals is None:
            # Show one decimal by default if values is < 1%
            if abs(x) < 0.01:
                x = round(x, 1 + 2)
            else:
                x = round(x, 2)
        else:
            x = round(x, self.decimals + 2)

        return format_percent(x, locale=self.l, decimal_quantization=False)

    def temperature_short(self, x, *args, **kwargs):
        """Format a temperature in deegrees, without scale letter."""
        decimals = self.decimals
        if decimals is None:
            decimals = 1

        x = round(Decimal(x), decimals)
        str = format_unit(x, 'temperature-generic', "short", locale=self.l)
        return str

    def temperature(self, x, *args, **kwargs):
        """Format a temperature in deegrees, with scale letter."""
        decimals = self.decimals
        if decimals is None:
            decimals = 1

        scale = "temperature-{}".format(self.scale)
        x = round(Decimal(x), decimals)
        str = format_unit(x, scale, "short", locale=self.l)
        return str

    def number(self, x, *args, **kwargs):
        """Format as number.

        :param decimals (int): number of decimals.
        """
        decimals = self.decimals
        if decimals is None:
            # Default roundings
            if abs(x) < 0.1:
                decimals = 2
            elif abs(x) < 1:
                decimals = 1
            else:
                decimals = 0
        x = round(Decimal(x), decimals)
        return format_decimal(x, locale=self.l)

    def short_month(self, x, *args, **kwargs):
        """Get a short month string, e.g. 'Jan', from a number.

        Numbers above 12 will wrap
        """
        if x > 12:
            x = x % 12 + 1
        return self.l.months['format']['abbreviated'][x]

    def month(self, x, *args, **kwargs):
        """Get a month string from a number.

        Numbers above 12 will wrap
        """
        if x > 12:
            x = x % 12 + 1
        return self.l.months['format']['wide'][x]
