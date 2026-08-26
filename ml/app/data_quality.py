from datetime import datetime

def validate_snapshot(s):
 errors=[]
 if s.minute==0 and s.captured_at>s.kickoff:errors.append('PREMATCH_AFTER_KICKOFF')
 if s.available_at>s.decision_time:errors.append('POINT_IN_TIME_VIOLATION')
 if s.minute<0 or s.minute>130:errors.append('INVALID_MINUTE')
 for v in [s.xg_home,s.xg_away,s.possession_home,s.ppda_home]:
  if v<0:errors.append('NEGATIVE_VALUE')
 if not 0<=s.possession_home<=100:errors.append('INVALID_POSSESSION')
 if s.shots_on_target>s.shots:errors.append('SOT_GT_SHOTS')
 if s.home_goals<0 or s.away_goals<0:errors.append('NEGATIVE_SCORE')
 if s.source_timestamp and abs((s.captured_at-s.source_timestamp).total_seconds())>300:errors.append('STALE_SOURCE_TIMESTAMP')
 return errors

def score_snapshot(s):
 e=validate_snapshot(s);score=100-len(e)*15
 if s.source in ('manual','demo'):score-=5
 return max(0,min(100,score)),e
