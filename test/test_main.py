""" py.test tests for Newsworthycharts
"""
from newsworthycharts import Chart, SerialChart, CategoricalChart
from newsworthycharts.storage import DictStorage
from imghdr import what
from PIL import Image
from hashlib import md5
import numpy as np


def test_generating_png():
    container = {}
    ds = DictStorage(container)
    c = Chart(800, 600, storage=ds)
    c.render("test", "png")

    assert("png" in container)
    assert(what(container["png"]) == "png")


def test_image_size():
    container = {}
    ds = DictStorage(container)
    c = Chart(613, 409, storage=ds)
    c.render("test", "png")

    im = Image.open(container["png"])
    assert(im.size == (613, 409))


def test_setting_title():
    t1 = "Rosor i ett sprucket krus, är ändå alltid rosor"
    t2 = "Äntligen stod prästen i predikstolen!"

    c = Chart(800, 600)
    assert(c.title is None)

    # Set title by directly manipulating underlaying object
    c.fig.suptitle(t1)
    assert(c.title == t1)

    # Set title using setter
    c.title = t2
    assert(c.title == t2)


def test_meta_data():
    """ Check that adding data also updates metadata"""

    c = Chart(900, 600)
    c.data.append([("a", 5), ("b", 5.5), ("c", 6)])
    c.data.append([("a", 2), ("b", 3), ("d", 4)])
    assert(c.data.min_val == 2)
    assert(c.data.max_val == 6)
    assert(c.data.x_points == ["a", "b", "c", "d"])

    d = Chart(900, 600)
    d.data.append([("2018-01-01", 5), ("2018-02-01", 5.5), ("2018-03-01", 6)])
    d.data.append([("2018-01-01", 2), ("2018-02-01", 3)])
    assert(d.data.inner_min_x == "2018-01-01")
    assert(d.data.inner_max_x == "2018-02-01")
    assert(d.data.outer_min_x == "2018-01-01")
    assert(d.data.outer_max_x == "2018-03-01")


def test_language_tag_parsing():
    """ Language tags should be normalized """

    c = Chart(10, 10, language="sv-Latn-AX")
    assert(c.locale.language == "sv")
    assert(c.locale.territory == "AX")

    # underscore shuold work as separator
    c = Chart(10, 10, language="sv_AX")
    assert(c.locale.language == "sv")

    # a macro language tag should fallback to its default specific language
    c = Chart(10, 10, language="no")
    assert(c.locale.language == "nb")


def test_filled_values():
    """ When adding multiple series, missing values should be filled in """

    c = Chart(900, 600)
    c.data.append([("a", 5), ("b", 5.5), ("c", 6)])
    c.data.append([("a", 2), ("b", 3), ("d", 4)])
    assert(c.data.filled_values[1] == [2, 3, 3.5, 4])


def test_annotation_with_missing_values_series():
    """ The test makes sure a bug in _get_annotation_direction was fixed
    when series containes missing values.
    """
    c = SerialChart(900, 600)
    c.data.append([
        ("2018-01-01", 5),
        ("2018-02-01", 6),
        ("2018-03-01", None),
        ("2018-04-01", 5),
    ])
    c.type = "line"
    c.highlight = "2018-04-01"
    c._apply_changes_before_rendering()


def test_categorical_chart_with_missing_data():
    c = CategoricalChart(900, 600)
    c.data.append([
        ("2018-01-01", 5),
        ("2018-02-01", 6),
        ("2018-03-01", None),
        ("2018-04-01", 5),
    ])
    c._apply_changes_before_rendering()


def test_very_many_bars():
    container = {}
    ds = DictStorage(container)
    s = SerialChart(300, 300, storage=ds)
    s2 = SerialChart(800, 300, storage=ds)
    long_data = [["1955-01-01", 0.3],["1956-01-01", 0.1],["1957-01-01", 0.3],["1958-01-01", 0.3],["1959-01-01", 0.3],["1960-01-01", 0.3],["1961-01-01", 0.3],["1962-01-01", 0.3],["1963-01-01", 0.3],["1964-01-01", 0.3],["1965-01-01", 0.3],["1966-01-01", 0.3],["1967-01-01", 0.3],["1968-01-01", 0.3],["1969-01-01", 0.3],["1970-01-01", 0.3],["1971-01-01", 0.3],["1972-01-01", 0.3],["1973-01-01", 0.3],["1974-01-01", 0.3],["1975-01-01", 0.3],["1976-01-01", 0.3],["1977-01-01", 0.3],["1978-01-01", 0.3],["1979-01-01", 0.3],["1980-01-01", 0.3],["1981-01-01", 0.3],["1982-01-01", 0.3],["1983-01-01", 0.3],["1984-01-01", 0.3],["1985-01-01", 0.3],["1986-01-01", 0.3],["1987-01-01", 0.3],["1988-01-01", 0.3],["1989-01-01", 0.3],["1990-01-01", 0.3],["1991-01-01", 0.3],["1992-01-01", 0.3],["1993-01-01", 0.3],["1994-01-01", 0.3],["1995-01-01", 0.3],["1996-01-01", 0.3],["1997-01-01", 0.3],["1998-01-01", 0.3],["1999-01-01", 0.3],["2000-01-01", 0.3],["2001-01-01", 0.3],["2002-01-01", 0.3],["2003-01-01", 0.3],["2004-01-01", 0.3],["2005-01-01", 0.3],["2006-01-01", 0.3],["2007-01-01", 0.3],["2008-01-01",None],["2009-01-01",None],["2010-01-01",None],["2011-01-01",None],["2012-01-01",None],["2013-01-01",0.091],["2014-01-01",None],["2015-01-01",0.145],["2016-01-01",0.14800000000000002],["2017-01-01",0.106],["2018-01-01",0.08]]
    s.data.append(long_data)
    s2.data.append(long_data)

    s.bar_width = 0.5
    s.render("test", "png")
    v1 = Image.open(container["png"])

    s.bar_width = 1
    s.render("test", "png")
    v2 = Image.open(container["png"])

    s2.render("test", "png")
    v3 = Image.open(container["png"])

    # bar_width should be ignored if there is not enough room for putting
    # space around all bars

    # These should look different
    # assert(np.sum(np.array(v1) == np.array(v3)) < 100)
    # These should look more or less the same
    assert(np.sum(np.array(v2) == np.array(v1)) > 300000)


def test_checksum_png():
    container = {}
    ds = DictStorage(container)
    c = SerialChart(800, 600, storage=ds)
    c.title = "Sex laxar i en laxask"
    c.caption = "This chart was brought\n to you by Örkeljunga Åminne"
    c.type = "line"
    c.data.append([
        ("2018-01-01", 5),
        ("2018-02-01", 6),
        ("2018-03-01", 1),
        ("2018-04-01", 5),
        ("2018-05-01", 5.6),
    ])
    c.data.append([
        ("2018-01-01", 2),
        ("2018-02-01", 0.5),
        ("2018-03-01", 3),
        ("2018-04-01", 1),
    ])
    c.render("test", "png")
    m = md5()
    m.update(container["png"].getvalue())

    assert(m.hexdigest() == "209c5addae84a2471d78605f6278e29f")
