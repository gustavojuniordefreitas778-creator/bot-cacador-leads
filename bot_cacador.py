"""Find OpenStreetMap businesses without a website and extract phone/email.

This tool creates a reviewable CSV for lead generation.
"""

from __future__ import annotations

import argparse
import csv
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "BotCacador/1.0 (OpenStreetMap lead research; contact: project operator)"
LOG = logging.getLogger("bot_cacador")


@dataclass(frozen=True)
class City:
    name: str
    country: str


# Dicionário expandido com as principais cidades e capitais do Brasil e Paraguai
CITIES = {
    "Foz do Iguaçu": City("Foz do Iguaçu", "Brasil"),
    "Ciudad del Este": City("Ciudad del Este", "Paraguai"),
    "Curitiba": City("Curitiba", "Brasil"),
    "São Paulo": City("São Paulo", "Brasil"),
    "Rio de Janeiro": City("Rio de Janeiro", "Brasil"),
    "Brasília": City("Brasília", "Brasil"),
    "Asunción": City("Asunción", "Paraguai"),
    "Encarnación": City("Encarnación", "Paraguai"),
}

DEFAULT_CITIES = ("Foz do Iguaçu", "Ciudad del Este", "Curitiba", "São Paulo", "Asunción")


def build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        backoff_factor=2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"POST"}),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": USER_AGENT})
    return session


def make_query(city_name: str) -> str:
    safe_name = city_name.replace("\\", "\\\\").replace('"', '\\"')
    return f"""[out:json][timeout:90];
area["name"~"^{safe_name}$"]["boundary"="administrative"]->.city;
(
  nwr["shop"]["name"]["website"!~"."]["contact:website"!~"."](area.city);
  nwr["amenity"~"^(restaurant|cafe|bar|fast_food|beauty_salon|hairdresser|dentist|clinic|pharmacy|doctors|veterinary|car_repair|car_wash|hotel|guest_house|bakery|bank|fitness_centre)$"]["name"]["website"!~"."]["contact:website"!~"."](area.city);
  nwr["craft"]["name"]["website"!~"."]["contact:website"!~"."](area.city);
);
out center tags;"""


def request_city(session: requests.Session, city: City) -> list[dict[str, Any]]:
    try:
        response = session.post(
            OVERPASS_URL,
            data={"data": make_query(city.name)},
            timeout=(15, 120),
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as error:
        raise RuntimeError(f"Falha ao consultar {city.name}: {error}") from error

    elements = payload.get("elements")
    if not isinstance(elements, list):
        raise RuntimeError(f"Resposta inválida da Overpass API para {city.name}.")
    return elements


def clean_cell(value: Any) -> str:
    """Prevent spreadsheet formula execution in exported text fields."""
    text = str(value or "").strip()
    if text.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + text
    return text


def element_to_row(element: dict[str, Any], city: City) -> dict[str, str] | None:
    tags = element.get("tags")
    if not isinstance(tags, dict):
        return None
    name = str(tags.get("name", "")).strip()
    if not name or tags.get("website") or tags.get("contact:website"):
        return None

    location = element.get("center") or element
    latitude = location.get("lat")
    longitude = location.get("lon")
    if latitude is None or longitude is None:
        return None

    category = tags.get("shop") or tags.get("amenity") or tags.get("craft") or "business"
    
    # Extração segura de telefone e e-mail cadastrados no OSM
    telefone = tags.get("phone") or tags.get("contact:phone") or tags.get("mobile") or ""
    email = tags.get("email") or tags.get("contact:email") or ""

    element_type = str(element.get("type", ""))
    element_id = str(element.get("id", ""))
    if element_type not in {"node", "way", "relation"} or not element_id:
        return None

    return {
        "nome": clean_cell(name),
        "cidade": city.name,
        "pais": city.country,
        "categoria": clean_cell(category),
        "telefone": clean_cell(telefone),
        "email": clean_cell(email),
        "latitude": str(latitude),
        "longitude": str(longitude),
        "osm": f"https://www.openstreetmap.org/{element_type}/{element_id}",
    }


def find_businesses(city_names: list[str]) -> list[dict[str, str]]:
    session = build_session()
    rows: dict[str, dict[str, str]] = {}
    for index, city_name in enumerate(city_names):
        city = CITIES[city_name]
        LOG.info("Consultando estabelecimentos em %s (%s)", city.name, city.country)
        elements = request_city(session, city)
        for element in elements:
            row = element_to_row(element, city)
            if row:
                rows[row["osm"]] = row
        LOG.info("%s: %d estabelecimentos sem site encontrados", city.name, len(elements))
        if index < len(city_names) - 1:
            time.sleep(3)
    return list(rows.values())


def write_csv(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Novas colunas incluindo telefone e email
    fields = ("nome", "cidade", "pais", "categoria", "telefone", "email", "latitude", "longitude", "osm")
    with output_path.open("w", newline="", encoding="utf-8-sig") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera uma lista CSV de negócios no OSM sem site cadastrado."
    )
    parser.add_argument(
        "--cities",
        nargs="+",
        choices=tuple(CITIES),
        default=list(DEFAULT_CITIES),
        help="Cidades suportadas.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("leads.csv"),
        help="Caminho do CSV de saída (padrão: leads.csv).",
    )
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()
    try:
        rows = find_businesses(args.cities)
        write_csv(rows, args.output)
    except (OSError, RuntimeError) as error:
        LOG.error("%s", error)
        return 1
    LOG.info("CSV salvo em %s (%d registros)", args.output, len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
