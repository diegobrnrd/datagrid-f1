"""Busca de imagens SVG dos traçados de circuitos."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd

ASSETS_CIRCUITS_DIR = Path(__file__).resolve().parent.parent / "assets" / "circuits"
DEFAULT_CIRCUIT_IMAGE_VARIANT = "white-outline"

CIRCUIT_ALIASES = {
    "donington-park": "donington",
    "jose-carlos-pace": "interlagos",
    "nelson-piquet": "jacarepagua",
}


def slugify(value: object) -> str:
    """Converte um texto para slug ASCII seguro para busca de arquivos."""
    normalized = unicodedata.normalize("NFKD", str(value or ""))
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")


def _candidate_slugs(circuit_row: pd.Series) -> list[str]:
    circuit_slug = slugify(circuit_row.get("name"))
    place_slug = slugify(circuit_row.get("place_name"))

    candidates = [
        CIRCUIT_ALIASES.get(circuit_slug),
        CIRCUIT_ALIASES.get(place_slug),
        circuit_slug,
        place_slug,
    ]
    return [candidate for candidate in candidates if candidate]


def get_available_circuit_layouts(
    circuit_row: pd.Series,
    variant_key: str = DEFAULT_CIRCUIT_IMAGE_VARIANT,
) -> list[Path]:
    """Retorna imagens de traçado disponíveis para um circuito e variante visual."""
    variant_folder = ASSETS_CIRCUITS_DIR / variant_key
    if not variant_folder.exists():
        return []

    for slug in _candidate_slugs(circuit_row):
        matches = sorted(variant_folder.glob(f"{slug}-*.svg"))
        if matches:
            return matches

    return []
