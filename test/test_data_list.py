from newsworthycharts.lib.datalist import DataList


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
    assert(stacked_values[0] == 1 + 2)
    assert(stacked_values[1] == 2 + 0)
    assert(stacked_values[2] == 5 + 10)

    assert(dl.stacked_max_val == 15)
