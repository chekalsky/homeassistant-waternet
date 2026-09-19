"""Fetch and parse Waternet household drinking-water tariffs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import re

TARIFF_URL = (
    "https://www.waternet.nl/service-en-contact/drinkwater/kosten/met-watermeter/"
)
USER_AGENT = (
    "HomeAssistant-Waternet/0.1.0 (+https://github.com/chekalsky/homeassistant-waternet)"
)

_YEAR = re.compile(r"Wat betaalt u in (\d{4})", re.IGNORECASE)
_WATER = re.compile(r"€\s*([\d.,]+)\s*per\s*m3", re.IGNORECASE)
_STANDING = re.compile(r"€\s*([\d.,]+)\s*vaste kosten", re.IGNORECASE)
_BOL = re.compile(
    r"€\s*([\d.,]+)[^€]{0,80}(?:leidingwater|\(bol\))", re.IGNORECASE
)
_VAT = re.compile(r"([\d.,]+)\s*%\s*btw", re.IGNORECASE)


@dataclass(frozen=True)
class Tariffs:
    """Household volumetric tariffs from the Waternet rates page."""

    year: int
    water_eur_m3: float
    bol_eur_m3: float
    vat_percent: float
    standing_charge_eur_year: float

    @property
    def price_per_m3(self) -> float:
        """EUR/m³ including BOL and VAT, excluding standing charge."""
        return (self.water_eur_m3 + self.bol_eur_m3) * (1 + self.vat_percent / 100)

    @property
    def price_per_liter(self) -> float:
        """EUR/L including BOL and VAT, excluding standing charge."""
        return self.price_per_m3 / 1000

    @property
    def standing_charge_incl_vat(self) -> float:
        """EUR/year standing charge including VAT."""
        return self.standing_charge_eur_year * (1 + self.vat_percent / 100)


def _nl_decimal(text: str) -> float:
    return float(text.strip().replace(".", "").replace(",", "."))


def _to_text(html: str) -> str:
    html = html.replace("\u00a0", " ")
    html = re.sub(r"&nbsp;", " ", html, flags=re.IGNORECASE)
    html = re.sub(r"&euro;|&#8364;|&#x20ac;", "€", html, flags=re.IGNORECASE)
    html = re.sub(r"<sup>\s*3\s*</sup>", "3", html, flags=re.IGNORECASE)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html)


def parse_tariffs(html: str) -> Tariffs:
    """Extract 2026-style household tariffs from the Waternet rates HTML."""
    text = _to_text(html)
    year_match = _YEAR.search(text)
    if not year_match:
        raise ValueError("tariff year not found")

    chunk = text[year_match.end() : year_match.end() + 900]

    def _need(pattern: re.Pattern[str], label: str) -> str:
        match = pattern.search(chunk)
        if not match:
            raise ValueError(f"{label} not found")
        return match.group(1)

    return Tariffs(
        year=int(year_match.group(1)),
        water_eur_m3=_nl_decimal(_need(_WATER, "water price")),
        bol_eur_m3=_nl_decimal(_need(_BOL, "BOL")),
        vat_percent=_nl_decimal(_need(_VAT, "VAT")),
        standing_charge_eur_year=_nl_decimal(_need(_STANDING, "standing charge")),
    )


async def fetch_tariffs(session: Any) -> Tariffs:
    """Download the Waternet rates page and parse it."""
    import aiohttp

    timeout = aiohttp.ClientTimeout(total=30)
    async with session.get(
        TARIFF_URL,
        timeout=timeout,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html"},
    ) as response:
        response.raise_for_status()
        return parse_tariffs(await response.text())
