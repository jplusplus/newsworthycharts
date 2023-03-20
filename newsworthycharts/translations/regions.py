import csv

# Translate Newsworthy region codes
with open("newsworthycharts/translations/se_municipalities.csv") as f:
    NW_MUNI_TO_CLDR = { x["nw_id"]: x["cldr"] for x in csv.DictReader(f) }
