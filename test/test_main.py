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
