#!/usr/bin/env python3
"""Malý bežec, ktorý importuje funkciu pozícií_to_pdf a generuje vzorku PDF
Tento bežec je bezpečne prevádzkovať lokálne a nenazýva API SAXO.
"""
import os
import sys

here = os.path.dirname(__file__)
if here not in sys.path:
    sys.path.insert(0, here)

try:
    from saxo_demo02_positions_to_pdf import positions_to_pdf, HAVE_REPORTLAB
except Exception as e:
    print("Failed importing module:", e)
    sys.exit(2)

if not HAVE_REPORTLAB:
    print("ReportLab not available. Please install dependencies (see requirements.txt).")
    sys.exit(3)

# sample data with two mock positions
sample = {
    "Data": [
        {
            "PositionBase": {"AccountId": 12345, "Uic": 7700, "AssetType": "Stock", "Amount": 10, "OpenPrice": 100.0},
            "DisplayAndFormat": {"Symbol": "AAPL"},
            "PositionView": {"CurrentPrice": 150.0, "Exposure": 1500.0, "ProfitLossOnTrade": 500.0}
        },
        {
            "PositionBase": {"AccountId": 12345, "Uic": 1234, "AssetType": "Bond", "Amount": 5, "OpenPrice": 1000.0},
            "DisplayAndFormat": {"Symbol": "GOVT"},
            "PositionView": {"CurrentPrice": 1010.0, "Exposure": 5050.0, "ProfitLossOnTrade": 50.0}
        }
    ]
}

out_pdf = os.path.join(here, "sample_positions.pdf")

try:
    positions_to_pdf(sample, out_pdf)
    print(f"Sample PDF written: {out_pdf}")
except Exception as e:
    print("Failed to generate PDF:", e)
    sys.exit(4)
