def compare(champion,challenger):
 margin=.005;c=champion.get('oos',{'logloss':champion.get('oos_logloss',999),'brier':champion.get('oos_brier',999)});n=challenger.get('oos',{'logloss':challenger.get('oos_logloss',999),'brier':challenger.get('oos_brier',999)})
 return {'promote':challenger.get('oos_sample',challenger.get('sample',0))>=100 and n.get('logloss',999)<=c.get('logloss',champion.get('oos_logloss',999))-margin and n.get('brier',999)<=c.get('brier',champion.get('oos_brier',999))+margin and not challenger.get('final_holdout_used',False)}
