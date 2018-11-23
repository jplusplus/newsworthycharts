""" py.test tests for Newsworthycharts
"""
from newsworthycharts import Chart, SerialChart, CategoricalChart
from newsworthycharts.storage import DictStorage
from imghdr import what
from PIL import Image


def test_generating_png():
    container = {}
    ds = DictStorage(container)
    c = Chart(800, 600, storage=ds)
    c.render("test", "png")

    assert("png" in container)
    assert(what(container["png"]) == "png")


def test_file_size():
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
