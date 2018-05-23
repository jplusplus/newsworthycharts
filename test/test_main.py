""" py.test tests for Newsworthycharts
"""
from newsworthycharts import Chart
from newsworthycharts import LocalStorage, S3Storage
from newsworthycharts.storage import DictStorage
from imghdr import what


def test_generating_png():

    container = {}
    ds = DictStorage(container)
    c = Chart(600, 800, storage=ds)
    c.render("test", "png")

    assert("png" in container)
    assert(what(container["png"]) == "png")
