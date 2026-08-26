from ml.app.research.cycle15.run_cycle15 import nonpit_h005

def test_nonpit_h005_is_explicitly_nonpit_research_only():
    r=nonpit_h005()
    assert r['status']=='NON_PIT_RESEARCH_ONLY'
    assert r['bets']>0
