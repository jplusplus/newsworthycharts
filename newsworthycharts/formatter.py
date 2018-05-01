"""
 Module for doing (very) simple i18n work.
"""
from babel.numbers import format_decimal, format_percent, Locale
from decimal import Decimal


class Formatter(object):
    """
     A formatter for a specific language and locale.
     Contains some methods for number and text formatting.

     Heavier i18n work should be before involving newsworthycharts.
     Usage:

      >>> fmt = Formatter("sv-SE")
      >>> fmt.percent(0.14)
      "14 %"
    """
    def __init__(self, lang, decimals=None):
        """
        :param decimals (int): force formatting to N number of decimals
        """
        self.l = Locale.parse(lang.replace("-", "_"))
        self.language = self.l.language
        self.decimals = decimals

    def __repr__(self):
        return "Formatter: " + repr(self.l)

    def __str__(self):
        return self.l.get_display_name()

    def percent(self, x, *args, **kwargs):

        if self.decimals is None:
            # Show one decimal by default if values is < 1%
            if abs(x) < 0.01:
                x = round(x, 1)
        else:
            x = round(x, self.decimals)

        return format_percent(x, locale=self.l)

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

    def month(self, x):
        return self.l.months['format']['wide'][x]
