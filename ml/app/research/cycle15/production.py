from __future__ import annotations

def promotion_gate(metrics: dict) -> dict:
    reasons=[]
    if metrics.get('pit_events',0)<100: reasons.append('PIT_SAMPLE_LT_100')
    if metrics.get('oos_bets',0)<100: reasons.append('OOS_SAMPLE_LT_100')
    if metrics.get('clv_mean',0) <= 0: reasons.append('CLV_NOT_POSITIVE')
    if metrics.get('walk_forward_folds',0)<5: reasons.append('WALK_FORWARD_LT_5')
    if metrics.get('robustness')!='PASS': reasons.append('ROBUSTNESS_NOT_PASS')
    return {'production_infrastructure':'READY_FOR_PAPER_OR_SHADOW','trading_approved':False,'real_money':'DISABLED','reasons':reasons}
