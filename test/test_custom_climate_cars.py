from newsworthycharts.custom.climate_cars import ClimateCarsYearlyEmissionsTo2030, ClimateCarsCO2BugdetChart
from newsworthycharts.storage import LocalStorage


OUTPUT_DIR = "test/rendered_charts"
local_storage = LocalStorage(OUTPUT_DIR)


def test_lines_to_2030_target():
    
    chart_obj = {
        "data": [[
            (1990, 12.714),
            (1991, 12.906),
            (1992, 13.236),
            (1993, 12.583),
            (1994, 12.764),
            (1995, 12.985),
            (1996, 12.882),
            (1997, 12.701),
            (1998, 12.505),
            (1999, 12.664),
            (2000, 12.576),
            (2001, 12.697),
            (2002, 12.928),
            (2003, 12.89),
            (2004, 12.793),
            (2005, 12.69),
            (2006, 12.533),
            (2007, 12.644),
            (2008, 12.196),
            (2009, 12.24),
            (2010, 12.011),
            (2011, 11.696),
            (2012, 11.179),
            (2013, 10.956),
            (2014, 10.781),
            (2015, 11.01),
            (2016, 10.744),
            (2017, 10.54),
            (2018, 10.4),
            (2019, 10.081)
        ], [
            (2019, 10.081),
            (2021, 8.288377148676176),
            (2022, 8.590662391139025),
            (2023, 8.258127233506125),
            (2024, 7.925851201088261),
            (2025, 7.571961239370827),
            (2026, 7.212002017699526),
            (2027, 6.879744824091043),
            (2028, 6.519618791474232),
            (2029, 6.1062206187310375),
            (2030, 5.658419507276658),
            (2031, 5.239671152956407),
            (2032, 4.850027888917168),
            (2033, 4.485644238254316),
            (2034, 4.1420022003821),
            (2035, 3.818658630355081),
            (2036, 3.5095860989071808),
            (2037, 3.2160534560553677),
            (2038, 2.939987760367349),
            (2039, 2.684276205711731),
            (2040, 2.4540303131142656),
            (2041, 2.241428428455672),
            (2042, 2.044518293335075),
            (2043, 1.8606517407319143),
            (2044, 1.687996773131078),
            (2045, 1.5254140713301103),
        ], [
            (2019, 10.081),
            (2020, 8.63543024316014),
            (2021, 7.778910350837727),
            (2022, 7.50912156324886),
            (2023, 6.721059246391919),
            (2024, 6.026704530461344),
            (2025, 5.353247314069254),
            (2026, 4.657249428666031),
            (2027, 4.060956949433057),
            (2028, 3.629450059172238),
            (2029, 3.1385168971074857),
            (2030, 2.6145909402087413),
            (2031, 2.1701975926131465),
            (2032, 1.7769496660521598),
            (2033, 1.4352320466954795),
            (2034, 1.137884418262449),
            (2035, 0.8924724779861856),
            (2036, 0.6863860574009506),
            (2037, 0.4720174735482677),
            (2038, 0.2863750824626263),
            (2039, 0.1857368740967005),
            (2040, 0.1263029407320242),
            (2041, 0.0931109103490034),
            (2042, 0.0706022923741066),
            (2043, 0.0565690409721323),
            (2044, 0.0460014577309976),
            (2045, 0.0352404702477841),
        ]
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
        "width": 1024,
        "height": 700,
        "labels": [
            "Utsläppen\nfortsätter\nsom i dag",
            "Reduktion\ni linje med\nklimatmålet",
        ],
        "note": 'Klimatmålet innebär att transporternas utsläppens ska reduceras med 70 procent till år 2030 i förhållande till 2010. Scenario 1 är baserat på utsläppsdata för 2019, scenario 2 på en jämn utsläppsminskning till och med år 2030.',
        "series": [],
        "source": "scb",
        "subtitle": "Ackumulerade koldioxidutsl\u00e4pp fr\u00e5n transportsektorn i två olika scenarier",
        "title": "Klimatm\u00e5let inte tillr\u00e4ckligt f\u00f6r att h\u00e5lla koldioxidbudget",
        "caption": "Källa: Klimatsekretariatet (CO2-bugdet), Naturvårdsverket (historiska utsläpp), Newsworthy (scenarier)",
        "type": "line",
        "units": "number",
        "decimals": 0,
    }
    c = ClimateCarsCO2BugdetChart.init_from(chart_obj, storage=local_storage)

    c.render("custom_climate_cars_co2_budget", "png")

 