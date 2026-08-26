from .api_football import ApiFootballProvider
from .statsbomb_open import StatsBombOpenProvider

def build(source_id):
    if source_id=='api-football': return ApiFootballProvider()
    if source_id=='statsbomb-open-data': return StatsBombOpenProvider()
    raise KeyError(source_id)
