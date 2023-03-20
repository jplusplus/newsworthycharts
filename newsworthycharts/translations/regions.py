import csv
import os
HERE = os.path.dirname(__file__)

# Translate Newsworthy region codes
with open(os.path.join(HERE, "se_municipalities.csv")) as f:
    NW_MUNI_TO_CLDR = {
        x["nw_id"]: x["cldr"] for x in csv.DictReader(f)
    }
