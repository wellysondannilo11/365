from __future__ import annotations


def value_confidence(*, sample_size: int, source_quality: str, calibration_error: float | None, model_disagreement: float | None, robustness_pass_rate: float | None) -> str:
    if sample_size < 30 or source_quality not in {'PIT_EXACT', 'PIT_APPROXIMATE'}:
        return 'INSUFFICIENT DATA'
    score = 0
    if source_quality == 'PIT_EXACT': score += 2
    if calibration_error is not None and calibration_error <= 0.05: score += 2
    if model_disagreement is not None and model_disagreement <= 0.05: score += 2
    if robustness_pass_rate is not None and robustness_pass_rate >= 0.70: score += 2
    if sample_size >= 200: score += 2
    if score >= 8: return 'HIGH CONFIDENCE'
    if score >= 5: return 'MEDIUM CONFIDENCE'
    return 'LOW CONFIDENCE'
