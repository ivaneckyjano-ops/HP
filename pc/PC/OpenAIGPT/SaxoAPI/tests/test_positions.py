import os
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
from saxo_demo02_positions_to_pdf import positions_to_pdf, HAVE_REPORTLAB


def sample_data():
    return {"Data": [{
        "PositionBase": {"AccountId": 1, "Uic": 100, "AssetType": "Stock", "Amount": 2, "OpenPrice": 10},
        "DisplayAndFormat": {"Symbol": "TST"},
        "PositionView": {"CurrentPrice": 12, "Exposure": 24, "ProfitLossOnTrade": 4}
    }]}


def test_positions_to_pdf(tmp_path):
    out = tmp_path / "out.pdf"
    data = sample_data()
    res = positions_to_pdf(data, str(out))
    if HAVE_REPORTLAB:
        assert os.path.exists(str(out))
    else:
        # should return HTML path
        assert res.endswith('.html')
        assert os.path.exists(res)
