from newsworthycharts.custom.climate_cars import ClimateCarsYearlyEmissionsTo2030, ClimateCarsCO2BugdetChart
from newsworthycharts.storage import LocalStorage


OUTPUT_DIR = "test/rendered_charts"
local_storage = LocalStorage(OUTPUT_DIR)


def test_lines_to_2030_target():
    observed = [('2000-01-01', 12.519),
                ('2001-01-01', 12.622),
                ('2002-01-01', 12.865),
                ('2003-01-01', 12.845),
                ('2004-01-01', 12.757),
                ('2005-01-01', 12.651),
                ('2006-01-01', 12.485),
                ('2007-01-01', 12.585),
                ('2008-01-01', 12.122),
                ('2009-01-01', 12.136),
                ('2010-01-01', 11.892000000000001),
                ('2011-01-01', 11.545),
                ('2012-01-01', 10.994000000000002),
                ('2013-01-01', 10.775),
                ('2014-01-01', 10.645999999999999),
                ('2015-01-01', 10.764000000000001),
                ('2016-01-01', 10.508),
                ('2017-01-01', 10.252),
                ('2018-01-01', 10.007),
    ]
    proj1 = [
            ('2018-01-01', 10.007),
            ('2019-01-01', 9.8179657604514),
            ('2020-01-01', 9.608940985035355),
            ('2021-01-01', 9.39767113216451),
            ('2022-01-01', 9.192712852919053),
            ('2023-01-01', 8.982294459789081),
            ('2024-01-01', 8.754982276852349),
            ('2025-01-01', 8.512300890435585),
            ('2026-01-01', 8.255139094690502),
            ('2027-01-01', 7.96753155887168),
            ('2028-01-01', 7.636931933932328),
            ('2029-01-01', 7.253945631547102),
            ('2030-01-01', 6.7983160616202865)
    ]
    proj2 = [
        ('2019-01-01', 9.8179657604514),
        ('2020-01-01', 9.607490278597078),
        ('2021-01-01', 9.392510237523977),
        ('2022-01-01', 9.180579690093461),
        ('2023-01-01', 8.958579546300985),
        ('2024-01-01', 8.713089139693023),
        ('2025-01-01', 8.442726594833344),
        ('2026-01-01', 8.144576517555915),
        ('2027-01-01', 7.797783239871976),
        ('2028-01-01', 7.382675120567321),
        ('2029-01-01', 6.880152972324297),
        ('2030-01-01', 6.257097746208816)
    ]
    chart_obj = {
        "data": [
            observed,
            proj1,
            proj2,
        ],
        "labels": [
            "Historiska",
            "Antar att 65 %\n av nya bilar är\nladdbara år 2030",
            "Antar 90 %\nladdbara år 2030",
        ],
        "width": 1024,
        "height": 760,
        "type": "line",
        "ymin": 0,
        "title": "Laddbara fordon tar oss inte till klimatmålet",
        "subtitle": "Årliga koldioxidutsläpp från personssektorn i två olika scenarier för elbilsförsäljning år 2030.",
        "note": "Scenarierna antar ökat trafikarbete med en procent per år. Biobränslen beaktas däremot inte.",
        "caption": "Källa: Natuvårdsverket / Newsworthy",
        "target": 3.56,
        "target_label": "Klimatmålet 2030"
    }
    c = ClimateCarsYearlyEmissionsTo2030.init_from(chart_obj, storage=local_storage)

    c.render("custom_climate_cars_lines_to_2030", "png")


def test_co2_budget_chart():
    chart_obj = {
        "line_annotations": [
            [
                "2024-09-12",
                93.63013100013671,
                "Med nuvarande utsläpp\növerskrider vi budget år 2024"
            ],
            [
                "2027-07-07",
                93.63013100013671,
                "Trots att vi klarar\nklimatmålet\nspräcker vi budget"
            ]
        ],
        "budget": 93.63013100013671,
        "budget_label": "Budgettak",
        "chart_engine": "ClimateCarsCO2budget",
        "data": [
            [
                [
                    2019,
                    0.0
                ],
                [
                    2020,
                    16.428
                ],
                [
                    2021,
                    32.856
                ],
                [
                    2022,
                    49.284000000000006
                ],
                [
                    2023,
                    65.712
                ],
                [
                    2024,
                    82.14
                ],
                [
                    2025,
                    98.568
                ],
                [
                    2026,
                    114.996
                ],
                [
                    2027,
                    131.424
                ],
                [
                    2028,
                    147.852
                ],
                [
                    2029,
                    164.28
                ],
                [
                    2030,
                    180.708
                ]
            ],
            [
                [
                    2019,
                    0.0
                ],
                [
                    2020,
                    15.026916597154901
                ],
                [
                    2021,
                    28.772243016551627
                ],
                [
                    2022,
                    41.34528134775107
                ],
                [
                    2023,
                    52.84601170907111
                ],
                [
                    2024,
                    63.365887284060356
                ],
                [
                    2025,
                    72.98856155224945
                ],
                [
                    2026,
                    81.79055349707937
                ],
                [
                    2027,
                    89.84185608070419
                ],
                [
                    2028,
                    97.20649282422671
                ],
                [
                    2029,
                    103.94302691926296
                ],
                [
                    2030,
                    110.10502691926297
                ]
            ]
        ],
        "height": 760,
        "labels": [
            "Utsläppen\nfortsätter\nsom i dag",
            "Reduktion\ni linje med\nklimatmålet",
        ],
        "measures": [],
        "note": 'Klimatmålet innebär att transporternas utsläppens ska reduceras med 70 procent till år 2030 i förhållande till 2010. Scenario 1 är baserat på utsläppsdata för 2019, scenario 2 på en jämn utsläppsminskning till och med år 2030.',
        "periodicity": "yearly",
        "series": [],
        "source": "scb",
        "subtitle": "Ackumulerade koldioxidutsl\u00e4pp fr\u00e5n transportsektorn i två olika scenarier",
        "title": "Klimatm\u00e5let inte tillr\u00e4ckligt f\u00f6r att h\u00e5lla koldioxidbudget",
        "caption": "Källa: Klimatsekretariatet (CO2-bugdet), Naturvårdsverket (historiska utsläpp), Newsworthy (scenarier)",
        "type": "line",
        "units": "count",
        "width": 1024
    }
    c = ClimateCarsCO2BugdetChart.init_from(chart_obj, storage=local_storage)

    c.render("custom_climate_cars_co2_budget", "png")

 