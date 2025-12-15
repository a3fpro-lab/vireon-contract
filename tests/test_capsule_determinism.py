from vireon_contract.cli import _demo_gray_scott_like

def test_demo_determinism_exact():
    s1 = _demo_gray_scott_like(seed=7, steps=80)
    s2 = _demo_gray_scott_like(seed=7, steps=80)
    assert s1 == s2
