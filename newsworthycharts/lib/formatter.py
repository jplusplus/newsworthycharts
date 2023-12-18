"""Module for doing (very) simple i18n work."""
from babel.numbers import format_decimal, Locale
from babel.units import format_unit
from babel.dates import format_date
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal


class Formatter(object):
    """A formatter for a specific language and locale.

    Contains some methods for number and text formatting.
    Heavier i18n work should be before involving newsworthycharts.
    Usage:

     >>> fmt = Formatter("sv-SE")
     >>> fmt.percent(0.14)
     "14 %"
    """

    def __init__(
        self,
        lang,
        decimals: int=None,
        force_decimals: bool=False,
        scale: str="celcius",
        na_str: str="-",
    ):
        """Create formatter for specific locale."""
        self.l = Locale.parse(lang.replace("-", "_"))  # NOQA
        self.language = self.l.language
        self.decimals = decimals
        self.scale = scale
        self.na_str = na_str
        self.force_decimals = force_decimals

    def __repr__(self):
        return "Formatter: " + repr(self.l)

    def __str__(self):
        return self.l.get_display_name()

    def date(self, x, pattern):
        """ Use a date pattern to format a number """
        date = datetime.fromisoformat(x)
        return format_date(date, pattern, locale=self.l)

    def percent(self, x, *args, **kwargs):
        if x is None:
            return self.na_str

        decimals = self.decimals
        if decimals is not None:
            # round to decimals, but use “school class rounding”
            x = Decimal(x).quantize(Decimal("0." + "0" * (decimals + 2)), rounding=ROUND_HALF_UP)

        pattern = self.l.percent_formats[None].pattern
        # override pattern, to enable additional decimals
        if self.force_decimals and (decimals is not None):
            # Pattern is something like '#,##0\xa0%' or '#,##0%'
            # We will add a decimal subpattern after the last digit
            pattern = pattern.rsplit("0", 1)
            pattern[1] = "." + "0" * decimals + pattern[1]
            pattern = "0".join(pattern)
        else:
            pattern = pattern.rsplit("0", 1)
            pattern[1] = ".#" + pattern[1]
            pattern = "0".join(pattern)
        string = format_decimal(x, locale=self.l, format=pattern)
        minus = self.l.number_symbols["latn"]["minusSign"]
        string = string.replace("-", minus)
        return string

    def temperature_short(self, x, *args, **kwargs):
        """Format a temperature in deegrees, without scale letter."""
        decimals = self.decimals
        if decimals is None:
            decimals = 1

        x = round(Decimal(x), decimals)
        string = format_unit(x, 'temperature-generic', "short", locale=self.l)
        minus = self.l.number_symbols["latn"]["minusSign"]
        string = string.replace("-", minus)
        # if x > 0:
        #     string = "+" + string
        return string

    def temperature(self, x, *args, **kwargs):
        """Format a temperature in deegrees, with scale letter."""
        decimals = self.decimals
        if decimals is None:
            decimals = 1

        scale = "temperature-{}".format(self.scale)
        x = round(Decimal(x), decimals)
        string = format_unit(x, scale, "short", locale=self.l)
        minus = self.l.number_symbols["latn"]["minusSign"]
        string = string.replace("-", minus)
        return string

    def number(self, x, *args, **kwargs):
        """Format as number.

        :param decimals (int): number of decimals.
        """
        if x is None:
            return self.na_str

        decimals = self.decimals
        if decimals is not None:
            # round to decimals, but use “school class rounding”
            x = Decimal(x).quantize(Decimal("0." + "0" * decimals), rounding=ROUND_HALF_UP)
        pattern = self.l.decimal_formats[None].pattern
        # override pattern, to enable additional decimals
        if self.force_decimals and decimals is not None:
            pattern = pattern.split(".")
            pattern[1] = "0" * decimals + pattern[1]
            pattern = ".".join(pattern)
        string = format_decimal(x, locale=self.l, format=pattern)
        minus = self.l.number_symbols["latn"]["minusSign"]
        string = string.replace("-", minus)
        return string

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
