def rank_opportunities(items):
    return sorted(items, key=lambda x:(x.get("score",0),x.get("ev",0),x.get("edge",0)), reverse=True)
