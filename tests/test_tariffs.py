"""Parser checks against the live 2026 Waternet rates HTML."""

from pathlib import Path

from tariffs import parse_tariffs

FIXTURE = Path(__file__).parent / "fixtures" / "met-watermeter.html"


def test_parse_2026_rates_page() -> None:
    tariffs = parse_tariffs(FIXTURE.read_text(encoding="utf-8"))
    assert tariffs.year == 2026
    assert tariffs.water_eur_m3 == 1.18
    assert tariffs.bol_eur_m3 == 0.437
    assert tariffs.vat_percent == 9.0
    assert tariffs.standing_charge_eur_year == 90.55
    assert round(tariffs.price_per_m3, 4) == 1.7625
    assert round(tariffs.price_per_liter, 6) == 0.001763
    assert round(tariffs.standing_charge_incl_vat, 2) == 98.70
