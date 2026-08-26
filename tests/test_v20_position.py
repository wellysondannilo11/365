from ml.app.v20.position import assess_position,reverse_candidate

def test_position_hold_reduce_exit():
    assert assess_position(entry_odds=2,current_odds=2.1,fair_probability=.60,stake_units=.5,remaining_minutes=30)['action']=='HOLD'
    assert assess_position(entry_odds=2,current_odds=1.80,fair_probability=.60,stake_units=.5,remaining_minutes=30)['action']=='REDUCE'
    assert assess_position(entry_odds=2,current_odds=4,fair_probability=.20,stake_units=.5,remaining_minutes=30)['action']=='EXIT'

def test_reverse_requires_independent_value():
    assert reverse_candidate(opposite_odds=2.5,opposite_probability=.46)['eligible']
    assert not reverse_candidate(opposite_odds=2.0,opposite_probability=.48)['eligible']
