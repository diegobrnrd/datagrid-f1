import re
import unicodedata
from pathlib import Path

import pandas as pd

ASSETS_CIRCUITS_DIR = Path(__file__).resolve().parent.parent / "assets" / "circuits"

CIRCUIT_ALIASES = {
    "donington-park": "donington",
    "jose-carlos-pace": "interlagos",
    "nelson-piquet": "jacarepagua",
}


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(value))
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")


def get_available_circuit_layouts(circuit_row: pd.Series, variant_key: str = "white-outline") -> list[Path]:
    circuit_slug = slugify(circuit_row["name"])
    place_slug = slugify(circuit_row["place_name"])
    variant_folder = ASSETS_CIRCUITS_DIR / variant_key

    candidate_slugs = [
        CIRCUIT_ALIASES.get(circuit_slug),
        CIRCUIT_ALIASES.get(place_slug),
        circuit_slug,
        place_slug,
    ]

    for slug in candidate_slugs:
        if not slug:
            continue

        matches = sorted(variant_folder.glob(f"{slug}-*.svg"))
        if matches:
            return matches

    return []