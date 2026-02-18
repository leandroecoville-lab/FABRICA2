from app.inventory import _kind_from_name

def test_kind_from_name():
    assert _kind_from_name("x.pdf") == "pdf"
    assert _kind_from_name("x.MD") == "md"
    assert _kind_from_name("x.json") == "json"
    assert _kind_from_name("x.xlsx") == "xlsx"
    assert _kind_from_name("x.unknown") == "other"
