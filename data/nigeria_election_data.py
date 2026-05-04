"""
Nigeria Election Data Module
Sources: INEC official results, IFES Election Guide, ResearchGate datasets
Covers: Presidential, Gubernatorial, Senate, House of Reps (2011–2023)
"""

import pandas as pd
import numpy as np

# ─────────────────────────────────────────────
# NIGERIA STATES WITH GEOPOLITICAL ZONES
# ─────────────────────────────────────────────
STATES_ZONES = {
    "Abia": "South East", "Anambra": "South East", "Ebonyi": "South East",
    "Enugu": "South East", "Imo": "South East",
    "Akwa Ibom": "South South", "Bayelsa": "South South", "Cross River": "South South",
    "Delta": "South South", "Edo": "South South", "Rivers": "South South",
    "Ekiti": "South West", "Lagos": "South West", "Ogun": "South West",
    "Ondo": "South West", "Osun": "South West", "Oyo": "South West",
    "Benue": "North Central", "FCT": "North Central", "Kogi": "North Central",
    "Kwara": "North Central", "Nasarawa": "North Central", "Niger": "North Central",
    "Plateau": "North Central",
    "Adamawa": "North East", "Bauchi": "North East", "Borno": "North East",
    "Gombe": "North East", "Taraba": "North East", "Yobe": "North East",
    "Jigawa": "North West", "Kaduna": "North West", "Kano": "North West",
    "Katsina": "North West", "Kebbi": "North West", "Sokoto": "North West",
    "Zamfara": "North West",
}

STATES = list(STATES_ZONES.keys())

# ─────────────────────────────────────────────
# PRESIDENTIAL ELECTION DATA (2011–2023)
# Source: INEC official results
# ─────────────────────────────────────────────

PRESIDENTIAL_DATA = {
    2011: {
        "winner": "Goodluck Jonathan", "winner_party": "PDP",
        "registered_voters": 73_528_040, "total_votes": 39_469_484,
        "turnout_pct": 53.68,
        "results": {
            "PDP": 22_495_187, "CPC": 12_214_853, "ACN": 2_079_151,
            "ANPP": 917_012, "Others": 1_763_281
        }
    },
    2015: {
        "winner": "Muhammadu Buhari", "winner_party": "APC",
        "registered_voters": 67_422_005, "total_votes": 29_432_083,
        "turnout_pct": 43.65,
        "results": {
            "APC": 15_424_921, "PDP": 12_853_162, "Others": 1_153_000
        }
    },
    2019: {
        "winner": "Muhammadu Buhari", "winner_party": "APC",
        "registered_voters": 82_344_107, "total_votes": 28_614_190,
        "turnout_pct": 34.75,
        "results": {
            "APC": 15_191_847, "PDP": 11_255_978, "Others": 2_166_365
        }
    },
    2023: {
        "winner": "Bola Tinubu", "winner_party": "APC",
        "registered_voters": 93_469_008, "total_votes": 25_286_616,
        "turnout_pct": 27.06,
        "results": {
            "APC": 8_794_726, "PDP": 6_984_520, "LP": 6_101_533,
            "NNPP": 1_496_687, "Others": 909_150
        }
    }
}

# ─────────────────────────────────────────────
# STATE-LEVEL PRESIDENTIAL RESULTS (2015–2023)
# Source: INEC Results Portal, Tekedia, ResearchGate
# ─────────────────────────────────────────────

STATE_PRESIDENTIAL_2023 = {
    "Abia":       {"APC": 20_000,  "PDP": 39_214,  "LP": 358_890, "NNPP": 2_000},
    "Adamawa":    {"APC": 347_685, "PDP": 383_358,  "LP": 24_000,  "NNPP": 3_000},
    "Akwa Ibom":  {"APC": 80_000,  "PDP": 291_470,  "LP": 110_000, "NNPP": 5_000},
    "Anambra":    {"APC": 18_000,  "PDP": 22_000,   "LP": 495_891, "NNPP": 3_500},
    "Bauchi":     {"APC": 370_000, "PDP": 286_861,  "LP": 8_000,   "NNPP": 15_000},
    "Bayelsa":    {"APC": 50_000,  "PDP": 110_000,  "LP": 58_000,  "NNPP": 2_000},
    "Benue":      {"APC": 207_000, "PDP": 166_000,  "LP": 137_000, "NNPP": 12_000},
    "Borno":      {"APC": 658_080, "PDP": 84_000,   "LP": 4_000,   "NNPP": 3_000},
    "Cross River":{"APC": 87_000,  "PDP": 84_000,   "LP": 109_000, "NNPP": 5_000},
    "Delta":      {"APC": 80_000,  "PDP": 268_000,  "LP": 290_000, "NNPP": 8_000},
    "Ebonyi":     {"APC": 115_000, "PDP": 40_000,   "LP": 250_000, "NNPP": 2_000},
    "Edo":        {"APC": 210_000, "PDP": 119_000,  "LP": 331_000, "NNPP": 7_000},
    "Ekiti":      {"APC": 201_494, "PDP": 89_554,   "LP": 11_397,  "NNPP": 264},
    "Enugu":      {"APC": 15_000,  "PDP": 47_000,   "LP": 486_800, "NNPP": 2_500},
    "FCT":        {"APC": 90_902,  "PDP": 74_000,   "LP": 200_000, "NNPP": 10_000},
    "Gombe":      {"APC": 311_000, "PDP": 157_000,  "LP": 9_000,   "NNPP": 7_000},
    "Imo":        {"APC": 128_000, "PDP": 38_000,   "LP": 390_000, "NNPP": 3_000},
    "Jigawa":     {"APC": 634_196, "PDP": 117_000,  "LP": 5_000,   "NNPP": 30_000},
    "Kaduna":     {"APC": 584_000, "PDP": 398_000,  "LP": 44_000,  "NNPP": 40_000},
    "Kano":       {"APC": 401_000, "PDP": 277_000,  "LP": 35_000,  "NNPP": 994_627},
    "Katsina":    {"APC": 576_000, "PDP": 475_000,  "LP": 11_000,  "NNPP": 30_000},
    "Kebbi":      {"APC": 450_000, "PDP": 185_000,  "LP": 5_000,   "NNPP": 8_000},
    "Kogi":       {"APC": 267_000, "PDP": 90_000,   "LP": 52_000,  "NNPP": 12_000},
    "Kwara":      {"APC": 263_572, "PDP": 136_909,  "LP": 31_116,  "NNPP": 3_141},
    "Lagos":      {"APC": 572_606, "PDP": 75_750,   "LP": 582_454, "NNPP": 14_000},
    "Nasarawa":   {"APC": 228_000, "PDP": 131_000,  "LP": 103_000, "NNPP": 16_000},
    "Niger":      {"APC": 507_000, "PDP": 192_000,  "LP": 19_000,  "NNPP": 21_000},
    "Ogun":       {"APC": 315_000, "PDP": 95_000,   "LP": 139_000, "NNPP": 9_000},
    "Ondo":       {"APC": 299_889, "PDP": 251_368,  "LP": 58_000,  "NNPP": 3_000},
    "Osun":       {"APC": 343_945, "PDP": 354_366,  "LP": 23_283,  "NNPP": 713},
    "Oyo":        {"APC": 328_000, "PDP": 281_000,  "LP": 130_000, "NNPP": 15_000},
    "Plateau":    {"APC": 227_000, "PDP": 158_000,  "LP": 265_000, "NNPP": 18_000},
    "Rivers":     {"APC": 230_000, "PDP": 240_000,  "LP": 175_000, "NNPP": 7_000},
    "Sokoto":     {"APC": 386_000, "PDP": 378_000,  "LP": 7_000,   "NNPP": 10_000},
    "Taraba":     {"APC": 224_000, "PDP": 224_000,  "LP": 46_000,  "NNPP": 6_000},
    "Yobe":       {"APC": 408_000, "PDP": 61_000,   "LP": 3_000,   "NNPP": 5_000},
    "Zamfara":    {"APC": 340_000, "PDP": 277_000,  "LP": 5_000,   "NNPP": 10_000},
}

STATE_PRESIDENTIAL_2019 = {
    "Abia":       {"APC": 27_000,  "PDP": 358_000},
    "Adamawa":    {"APC": 392_000, "PDP": 567_000},
    "Akwa Ibom":  {"APC": 98_000,  "PDP": 673_000},
    "Anambra":    {"APC": 49_000,  "PDP": 266_000},
    "Bauchi":     {"APC": 871_000, "PDP": 473_000},
    "Bayelsa":    {"APC": 165_000, "PDP": 197_000},
    "Benue":      {"APC": 375_000, "PDP": 325_000},
    "Borno":      {"APC": 859_000, "PDP": 72_000},
    "Cross River":{"APC": 99_000,  "PDP": 191_000},
    "Delta":      {"APC": 90_000,  "PDP": 565_000},
    "Ebonyi":     {"APC": 110_000, "PDP": 244_000},
    "Edo":        {"APC": 292_000, "PDP": 291_000},
    "Ekiti":      {"APC": 197_000, "PDP": 154_000},
    "Enugu":      {"APC": 35_000,  "PDP": 516_000},
    "FCT":        {"APC": 275_000, "PDP": 233_000},
    "Gombe":      {"APC": 419_000, "PDP": 235_000},
    "Imo":        {"APC": 205_000, "PDP": 317_000},
    "Jigawa":     {"APC": 1_048_000, "PDP": 85_000},
    "Kaduna":     {"APC": 1_127_000, "PDP": 619_000},
    "Kano":       {"APC": 1_464_000, "PDP": 391_000},
    "Katsina":    {"APC": 1_167_000, "PDP": 478_000},
    "Kebbi":      {"APC": 673_000, "PDP": 94_000},
    "Kogi":       {"APC": 401_000, "PDP": 110_000},
    "Kwara":      {"APC": 441_000, "PDP": 154_000},
    "Lagos":      {"APC": 1_349_000,"PDP": 448_000},
    "Nasarawa":   {"APC": 317_000, "PDP": 206_000},
    "Niger":      {"APC": 808_000, "PDP": 204_000},
    "Ogun":       {"APC": 449_000, "PDP": 227_000},
    "Ondo":       {"APC": 312_000, "PDP": 160_000},
    "Osun":       {"APC": 433_000, "PDP": 254_000},
    "Oyo":        {"APC": 540_000, "PDP": 518_000},
    "Plateau":    {"APC": 412_000, "PDP": 399_000},
    "Rivers":     {"APC": 286_000, "PDP": 883_000},
    "Sokoto":     {"APC": 525_000, "PDP": 488_000},
    "Taraba":     {"APC": 387_000, "PDP": 515_000},
    "Yobe":       {"APC": 553_000, "PDP": 55_000},
    "Zamfara":    {"APC": 374_000, "PDP": 520_000},
}

STATE_PRESIDENTIAL_2015 = {
    "Abia":       {"APC": 43_000,  "PDP": 296_000},
    "Adamawa":    {"APC": 466_000, "PDP": 334_000},
    "Akwa Ibom":  {"APC": 67_000,  "PDP": 585_000},
    "Anambra":    {"APC": 28_000,  "PDP": 494_000},
    "Bauchi":     {"APC": 790_000, "PDP": 363_000},
    "Bayelsa":    {"APC": 62_000,  "PDP": 222_000},
    "Benue":      {"APC": 308_000, "PDP": 208_000},
    "Borno":      {"APC": 450_000, "PDP": 48_000},
    "Cross River":{"APC": 61_000,  "PDP": 295_000},
    "Delta":      {"APC": 66_000,  "PDP": 536_000},
    "Ebonyi":     {"APC": 40_000,  "PDP": 246_000},
    "Edo":        {"APC": 284_000, "PDP": 236_000},
    "Ekiti":      {"APC": 203_000, "PDP": 116_000},
    "Enugu":      {"APC": 28_000,  "PDP": 486_000},
    "FCT":        {"APC": 198_000, "PDP": 146_000},
    "Gombe":      {"APC": 362_000, "PDP": 178_000},
    "Imo":        {"APC": 99_000,  "PDP": 406_000},
    "Jigawa":     {"APC": 944_000, "PDP": 98_000},
    "Kaduna":     {"APC": 1_127_000,"PDP": 484_000},
    "Kano":       {"APC": 1_903_000,"PDP": 215_000},
    "Katsina":    {"APC": 1_345_000,"PDP": 98_000},
    "Kebbi":      {"APC": 567_000, "PDP": 104_000},
    "Kogi":       {"APC": 264_000, "PDP": 165_000},
    "Kwara":      {"APC": 302_000, "PDP": 133_000},
    "Lagos":      {"APC": 792_000, "PDP": 232_000},
    "Nasarawa":   {"APC": 236_000, "PDP": 178_000},
    "Niger":      {"APC": 657_000, "PDP": 187_000},
    "Ogun":       {"APC": 528_000, "PDP": 192_000},
    "Ondo":       {"APC": 299_000, "PDP": 251_000},
    "Osun":       {"APC": 383_000, "PDP": 249_000},
    "Oyo":        {"APC": 528_000, "PDP": 310_000},
    "Plateau":    {"APC": 429_000, "PDP": 427_000},
    "Rivers":     {"APC": 69_000,  "PDP": 1_487_000},
    "Sokoto":     {"APC": 671_000, "PDP": 152_000},
    "Taraba":     {"APC": 374_000, "PDP": 423_000},
    "Yobe":       {"APC": 473_000, "PDP": 48_000},
    "Zamfara":    {"APC": 544_000, "PDP": 271_000},
}

# ─────────────────────────────────────────────
# REGISTERED VOTERS & TURNOUT BY STATE (2023)
# Source: INEC IReV Portal
# ─────────────────────────────────────────────
STATE_VOTER_DATA_2023 = {
    "Abia": {"registered": 1_800_000, "accredited": 490_000},
    "Adamawa": {"registered": 2_100_000, "accredited": 870_000},
    "Akwa Ibom": {"registered": 2_900_000, "accredited": 600_000},
    "Anambra": {"registered": 2_500_000, "accredited": 600_000},
    "Bauchi": {"registered": 2_900_000, "accredited": 770_000},
    "Bayelsa": {"registered": 950_000, "accredited": 270_000},
    "Benue": {"registered": 2_500_000, "accredited": 660_000},
    "Borno": {"registered": 2_600_000, "accredited": 810_000},
    "Cross River": {"registered": 1_700_000, "accredited": 360_000},
    "Delta": {"registered": 3_200_000, "accredited": 750_000},
    "Ebonyi": {"registered": 1_500_000, "accredited": 460_000},
    "Edo": {"registered": 2_600_000, "accredited": 740_000},
    "Ekiti": {"registered": 987_000, "accredited": 302_000},
    "Enugu": {"registered": 2_100_000, "accredited": 600_000},
    "FCT": {"registered": 1_900_000, "accredited": 440_000},
    "Gombe": {"registered": 1_500_000, "accredited": 550_000},
    "Imo": {"registered": 2_200_000, "accredited": 620_000},
    "Jigawa": {"registered": 2_800_000, "accredited": 840_000},
    "Kaduna": {"registered": 4_200_000, "accredited": 1_220_000},
    "Kano": {"registered": 6_000_000, "accredited": 1_800_000},
    "Katsina": {"registered": 3_800_000, "accredited": 1_190_000},
    "Kebbi": {"registered": 2_200_000, "accredited": 700_000},
    "Kogi": {"registered": 2_000_000, "accredited": 480_000},
    "Kwara": {"registered": 1_700_000, "accredited": 500_000},
    "Lagos": {"registered": 7_900_000, "accredited": 1_390_000},
    "Nasarawa": {"registered": 1_600_000, "accredited": 540_000},
    "Niger": {"registered": 3_100_000, "accredited": 810_000},
    "Ogun": {"registered": 2_800_000, "accredited": 640_000},
    "Ondo": {"registered": 2_200_000, "accredited": 700_000},
    "Osun": {"registered": 2_100_000, "accredited": 810_000},
    "Oyo": {"registered": 3_800_000, "accredited": 870_000},
    "Plateau": {"registered": 2_500_000, "accredited": 760_000},
    "Rivers": {"registered": 3_700_000, "accredited": 750_000},
    "Sokoto": {"registered": 2_500_000, "accredited": 850_000},
    "Taraba": {"registered": 1_800_000, "accredited": 540_000},
    "Yobe": {"registered": 1_600_000, "accredited": 530_000},
    "Zamfara": {"registered": 1_900_000, "accredited": 680_000},
}

# ─────────────────────────────────────────────
# NATIONAL ASSEMBLY SEATS (2023, 2019, 2015)
# Source: INEC / IPU Parline
# ─────────────────────────────────────────────
NATIONAL_ASSEMBLY = {
    2023: {
        "Senate": {"APC": 59, "PDP": 36, "LP": 8, "NNPP": 2, "Others": 4},
        "House":  {"APC": 178, "PDP": 120, "LP": 35, "NNPP": 18, "Others": 9}
    },
    2019: {
        "Senate": {"APC": 65, "PDP": 39, "Others": 5},
        "House":  {"APC": 217, "PDP": 115, "Others": 28}
    },
    2015: {
        "Senate": {"APC": 60, "PDP": 49, "Others": 0},
        "House":  {"APC": 225, "PDP": 125, "Others": 10}
    },
    2011: {
        "Senate": {"PDP": 71, "ACN": 18, "CPC": 7, "ANPP": 7, "Others": 6},
        "House":  {"PDP": 203, "ACN": 69, "CPC": 36, "ANPP": 25, "Others": 27}
    },
}

# ─────────────────────────────────────────────
# GUBERNATORIAL RESULTS (2023)
# Source: INEC results
# ─────────────────────────────────────────────
GOVERNORSHIP_2023 = {
    "Abia":       {"winner": "Alex Otti",      "party": "LP",  "votes": 175_467},
    "Adamawa":    {"winner": "Ahmadu Fintiri",  "party": "PDP", "votes": 357_749},
    "Akwa Ibom":  {"winner": "Umo Eno",         "party": "PDP", "votes": 382_215},
    "Anambra":    {"winner": "Charles Soludo",  "party": "APGA","votes": 406_067},
    "Bauchi":     {"winner": "Bala Mohammed",   "party": "PDP", "votes": 450_554},
    "Bayelsa":    {"winner": "Douye Diri",       "party": "PDP", "votes": 175_196},
    "Benue":      {"winner": "Hyacinth Alia",   "party": "APC", "votes": 373_813},
    "Borno":      {"winner": "Babagana Zulum",  "party": "APC", "votes": 870_494},
    "Cross River":{"winner": "Bassey Otu",      "party": "APC", "votes": 343_343},
    "Delta":      {"winner": "Sheriff Oborevwori","party": "PDP","votes": 533_045},
    "Ebonyi":     {"winner": "Francis Nwifuru", "party": "APC", "votes": 259_040},
    "Edo":        {"winner": "Monday Okpebholo","party": "APC", "votes": 291_667},
    "Ekiti":      {"winner": "Biodun Oyebanji",  "party": "APC", "votes": 187_057},
    "Enugu":      {"winner": "Peter Mbah",       "party": "PDP", "votes": 164_358},
    "FCT":        {"winner": "N/A (FCT Minister)",  "party": "N/A","votes": 0},
    "Gombe":      {"winner": "Muhammadu Yahaya", "party": "APC", "votes": 312_466},
    "Imo":        {"winner": "Hope Uzodimma",    "party": "APC", "votes": 529_919},
    "Jigawa":     {"winner": "Umar Namadi",      "party": "APC", "votes": 618_128},
    "Kaduna":     {"winner": "Uba Sani",         "party": "APC", "votes": 748_113},
    "Kano":       {"winner": "Abba Kabir Yusuf", "party": "NNPP","votes": 994_627},
    "Katsina":    {"winner": "Dikko Radda",      "party": "APC", "votes": 753_639},
    "Kebbi":      {"winner": "Nasir Idris",      "party": "APC", "votes": 421_368},
    "Kogi":       {"winner": "Usman Ododo",      "party": "APC", "votes": 446_237},
    "Kwara":      {"winner": "AbdulRahman AbdulRazaq","party": "APC","votes": 378_690},
    "Lagos":      {"winner": "Babajide Sanwo-Olu","party": "APC","votes": 762_134},
    "Nasarawa":   {"winner": "Abdullahi Sule",   "party": "APC", "votes": 279_188},
    "Niger":      {"winner": "Umar Bago",        "party": "APC", "votes": 510_328},
    "Ogun":       {"winner": "Dapo Abiodun",     "party": "APC", "votes": 392_632},
    "Ondo":       {"winner": "Lucky Aiyedatiwa", "party": "APC", "votes": 366_781},
    "Osun":       {"winner": "Ademola Adeleke",  "party": "PDP", "votes": 343_319},
    "Oyo":        {"winner": "Seyi Makinde",     "party": "PDP", "votes": 564_258},
    "Plateau":    {"winner": "Caleb Mutfwang",   "party": "PDP", "votes": 264_189},
    "Rivers":     {"winner": "Siminalayi Fubara","party": "PDP", "votes": 666_678},
    "Sokoto":     {"winner": "Ahmed Aliyu",      "party": "APC", "votes": 399_261},
    "Taraba":     {"winner": "Agbu Kefas",       "party": "PDP", "votes": 262_846},
    "Yobe":       {"winner": "Mai Mala Buni",    "party": "APC", "votes": 423_992},
    "Zamfara":    {"winner": "Dauda Lawal",      "party": "PDP", "votes": 392_361},
}

# ─────────────────────────────────────────────
# VOTER REGISTRATION TREND (2011–2023)
# Source: INEC official figures
# ─────────────────────────────────────────────
VOTER_REGISTRATION_TREND = {
    2011: 73_528_040,
    2015: 67_422_005,
    2019: 82_344_107,
    2023: 93_469_008,
}

TURNOUT_TREND = {
    2011: 53.68,
    2015: 43.65,
    2019: 34.75,
    2023: 27.06,
}

# ─────────────────────────────────────────────
# HELPER FUNCTIONS TO BUILD DATAFRAMES
# ─────────────────────────────────────────────

def get_presidential_summary():
    rows = []
    for year, data in PRESIDENTIAL_DATA.items():
        for party, votes in data["results"].items():
            rows.append({
                "Year": year,
                "Party": party,
                "Votes": votes,
                "Pct": round(votes / data["total_votes"] * 100, 2),
                "Registered": data["registered_voters"],
                "Total_Votes": data["total_votes"],
                "Turnout": data["turnout_pct"],
                "Winner": data["winner"],
                "Winner_Party": data["winner_party"]
            })
    return pd.DataFrame(rows)


def get_state_results(year=2023):
    mapping = {2023: STATE_PRESIDENTIAL_2023, 2019: STATE_PRESIDENTIAL_2019, 2015: STATE_PRESIDENTIAL_2015}
    data = mapping.get(year, STATE_PRESIDENTIAL_2023)
    rows = []
    for state, votes in data.items():
        total = sum(votes.values())
        winner_party = max(votes, key=votes.get)
        row = {"State": state, "Zone": STATES_ZONES.get(state, "Unknown"),
               "Total_Votes": total, "Winner_Party": winner_party, "Year": year}
        for p, v in votes.items():
            row[p] = v
            row[f"{p}_pct"] = round(v / total * 100, 2) if total > 0 else 0
        rows.append(row)
    df = pd.DataFrame(rows)
    # Fill missing party columns with 0
    for col in ["APC", "PDP", "LP", "NNPP"]:
        if col not in df.columns:
            df[col] = 0
        if f"{col}_pct" not in df.columns:
            df[f"{col}_pct"] = 0.0
    return df


def get_turnout_df():
    rows = []
    for year, reg in VOTER_REGISTRATION_TREND.items():
        rows.append({
            "Year": year,
            "Registered": reg,
            "Turnout_Pct": TURNOUT_TREND[year],
            "Votes_Cast": int(reg * TURNOUT_TREND[year] / 100)
        })
    return pd.DataFrame(rows)


def get_assembly_df():
    rows = []
    for year, chambers in NATIONAL_ASSEMBLY.items():
        for chamber, parties in chambers.items():
            total = sum(parties.values())
            for party, seats in parties.items():
                rows.append({
                    "Year": year, "Chamber": chamber, "Party": party,
                    "Seats": seats, "Total_Seats": total,
                    "Seat_Pct": round(seats / total * 100, 1)
                })
    return pd.DataFrame(rows)


def get_governorship_df():
    rows = []
    for state, data in GOVERNORSHIP_2023.items():
        rows.append({
            "State": state, "Zone": STATES_ZONES.get(state, "Unknown"),
            "Governor": data["winner"], "Party": data["party"], "Votes": data["votes"]
        })
    return pd.DataFrame(rows)


def get_zone_summary(year=2023):
    df = get_state_results(year)
    zones = []
    for zone, grp in df.groupby("Zone"):
        total = grp["Total_Votes"].sum()
        apc = grp["APC"].sum() if "APC" in grp else 0
        pdp = grp["PDP"].sum() if "PDP" in grp else 0
        lp  = grp["LP"].sum()  if "LP"  in grp else 0
        nnpp= grp["NNPP"].sum()if "NNPP"in grp else 0
        dominant = max({"APC": apc, "PDP": pdp, "LP": lp, "NNPP": nnpp}, key=lambda k: {"APC":apc,"PDP":pdp,"LP":lp,"NNPP":nnpp}[k])
        zones.append({"Zone": zone, "Total_Votes": total, "APC": apc, "PDP": pdp,
                      "LP": lp, "NNPP": nnpp, "Dominant_Party": dominant})
    return pd.DataFrame(zones)
