""" py.test tests for Newsworthycharts
"""
from newsworthycharts import Chart
from newsworthycharts import LocalStorage, S3Storage
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
    print(im.size)
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


def test_filled_values():
    """ Check the filled_values method"""

    c = Chart(900, 600)
    c.data.append([("a", 5), ("b", 5.5), ("c", 6)])
    c.data.append([("a", 2), ("b", 3), ("d", 4)])
    assert(c.data.filled_values[1] == [2, 3, 3.5, 4])
