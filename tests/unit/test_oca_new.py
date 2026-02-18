from app.oca import new_oca

def test_new_oca_minimal():
    o = new_oca(
        oca_id="oca-1",
        pack_target="pack1-x@1.0.0",
        oca_type="bugfix",
        summary="s",
        why="w",
        author="a",
        trace_id="t",
        reviewer="r",
    )
    assert o["oca_id"] == "oca-1"
    assert o["pack_target"] == "pack1-x@1.0.0"
    assert o["type"] == "bugfix"
    assert "risk" in o and "severity" in o["risk"]
