import csv,collections
from app.league_gate import league_gate
with open('../data.csv',newline='') as f: rows=list(csv.DictReader(f))
for league,items in __import__('itertools').groupby(sorted(rows,key=lambda x:x['league']),lambda x:x['league']):
 items=list(items); seasons=[x['season'] for x in items]; print(league,league_gate(league,seasons,len(items),95,min_rows=1))
