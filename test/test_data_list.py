from newsworthycharts.lib.datalist import DataList


def test_csv():
    s1 = [
        ("2018", 1),
        ("2019", 2),
    ]
    s2 = [
        ("2017", 3),
        ("2019", 4),
    ]
    dl = DataList()
    dl.append(s1)
    dl.append(s2)
    rows = dl.as_csv.split("\r\n")
    assert rows[0] == "2017,,3"
    assert rows[1] == "2018,1,"
    assert rows[2] == "2019,2,4"


def test_stacked_values():
    s1 = [
        ("A", 1),
        ("B", 2),
        ("C", 5),
    ]
    s2 = [
        ("A", 2),
        ("B", None),
        ("C", 10),
    ]

    dl = DataList()
    dl.append(s1)
    dl.append(s2)
    stacked_values = dl.stacked_values
    assert stacked_values[0] == 1 + 2
    assert stacked_values[1] == 2 + 0
    assert stacked_values[2] == 5 + 10
    assert dl.stacked_max_val == 15
