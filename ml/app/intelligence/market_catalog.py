from __future__ import annotations

MARKET_CATALOG = {
    'RESULT': ['H2H','DOUBLE_CHANCE','DNB','HT_FT','HT_RESULT','SECOND_HALF_RESULT'],
    'GOALS': ['TOTAL','TEAM_TOTAL_HOME','TEAM_TOTAL_AWAY','FIRST_HALF_TOTAL','SECOND_HALF_TOTAL'],
    'BTTS': ['BTTS','BTTS_OVER','BTTS_UNDER'],
    'HANDICAP': ['AH','EUROPEAN_HANDICAP','FIRST_HALF_AH','SECOND_HALF_AH'],
    'CORNERS': ['CORNER_TOTAL','CORNER_HOME','CORNER_AWAY','FIRST_HALF_CORNERS','SECOND_HALF_CORNERS'],
    'CARDS': ['CARD_TOTALS','CARD_HOME','CARD_AWAY','FIRST_HALF_CARDS','SECOND_HALF_CARDS'],
    'LIVE_NEXT_EVENT': ['NEXT_GOAL','NEXT_CARD','NEXT_CORNER'],
    'PLAYERS': ['PLAYER_GOAL','PLAYER_ASSIST','PLAYER_SHOTS','PLAYER_SOT','PLAYER_CARD'],
}

REQUIRED_LIVE_FIELDS = {
    'NEXT_GOAL': {'minute','score_home','score_away','source_timestamp','odds'},
    'NEXT_CARD': {'minute','cards_home','cards_away','source_timestamp','odds'},
    'NEXT_CORNER': {'minute','corners_home','corners_away','source_timestamp','odds'},
    'TOTAL': {'minute','score_home','score_away','source_timestamp','odds'},
    'AH': {'minute','score_home','score_away','source_timestamp','odds'},
    'H2H': {'minute','score_home','score_away','source_timestamp','odds'},
}

def supported_market_keys():
    return [m for group in MARKET_CATALOG.values() for m in group]

def market_requirements(market: str) -> set[str]:
    return REQUIRED_LIVE_FIELDS.get(str(market).upper(), {'source_timestamp','odds'})
