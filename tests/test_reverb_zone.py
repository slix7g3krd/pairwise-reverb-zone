import pytest
from audio import reverb_zone as mod

CASES = [
    ("weight_inner", "m.zone_weight(0.0, 1.0, 2.0) == approx(1.0)"),
    ("weight_outer", "m.zone_weight(2.0, 1.0, 2.0) == approx(0.0)"),
    ("weight_mid", "m.zone_weight(1.5, 1.0, 2.0) == approx(0.5)"),
    ("fade_start", "m.fade_both(0.0, 1.0, 0.0) == approx(0.0)"),
    ("fade_end", "m.fade_both(0.0, 1.0, 1.0) == approx(0.0)"),
    ("combine_sum", "m.combine_early_late(2.0, 3.0) == approx(5.0)"),
    ("indoor_wind", "m.indoor_outdoor(True, 0.8) == approx(0.0)"),
    ("outdoor_wind", "m.indoor_outdoor(False, 0.8) == approx(0.8)"),
    ("portal_open", "m.portal_lowpass(1.0, 1000.0) == approx(1000.0)"),
    ("portal_closed", "m.portal_lowpass(0.0, 1000.0) < 1000.0"),
    ("listener_zone", "m.zone_for_source('source', 'listener') == 'listener'"),
    ("pause_on", "m.pause_freeze(100, True) == 0"),
    ("pause_off", "m.pause_freeze(100, False) == 100"),
    ("overlap_sum", "sum(m.normalize_overlap([2.0, 2.0])) == approx(1.0)"),
    ("resample_same", "m.ir_resample(48000, 48000) == approx(1.0)")
]

@pytest.mark.parametrize("name,expr", CASES, ids=[c[0] for c in CASES])
def test_contract(name, expr):
    assert eval(expr, {"m": mod, "approx": pytest.approx})
