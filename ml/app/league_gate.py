def league_gate(league,seasons,rows,quality_score,min_seasons=3,min_rows=150):
    reasons=[]
    if len(set(seasons))<min_seasons: reasons.append('LESS_THAN_3_SEASONS')
    if rows<min_rows: reasons.append('INSUFFICIENT_SAMPLE')
    if quality_score<80: reasons.append('LOW_DATA_QUALITY')
    return {'eligible':not reasons,'league':league,'seasons':sorted(set(seasons)),'rows':rows,'quality_score':quality_score,'reasons':reasons}
