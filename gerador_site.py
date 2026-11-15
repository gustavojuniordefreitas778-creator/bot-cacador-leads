"""Render a customer landing page into a deployable static directory."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
TEMPLATE_PATH = ROOT / "templates" / "landing_page.html"
REQUIRED_FIELDS = ("nome_empresa", "cidade", "whatsapp", "descricao")
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CATEGORY_THEMES = {
    "default": {
        "label": "Atendimento local",
        "icon": "store",
        "primary": "#047857",
        "primary_dark": "#065f46",
        "secondary": "#0f766e",
        "accent": "#34d399",
        "hero": "#07111f",
        "tint": "#ecfdf5",
    },
    "automotive": {
        "label": "Automotivo",
        "icon": "car",
        "primary": "#dc2626",
        "primary_dark": "#b91c1c",
        "secondary": "#ea580c",
        "accent": "#f59e0b",
        "hero": "#171717",
        "tint": "#fff7ed",
    },
    "health": {
        "label": "Saúde e bem-estar",
        "icon": "medical",
        "primary": "#0284c7",
        "primary_dark": "#0369a1",
        "secondary": "#0f766e",
        "accent": "#2dd4bf",
        "hero": "#082f49",
        "tint": "#ecfeff",
    },
    "restaurant": {
        "label": "Gastronomia",
        "icon": "restaurant",
        "primary": "#c2410c",
        "primary_dark": "#9a3412",
        "secondary": "#b45309",
        "accent": "#fbbf24",
        "hero": "#431407",
        "tint": "#fff7ed",
    },
    "bakery": {
        "label": "Padaria e confeitaria",
        "icon": "bakery",
        "primary": "#b45309",
        "primary_dark": "#92400e",
        "secondary": "#c2410c",
        "accent": "#f59e0b",
        "hero": "#422006",
        "tint": "#fffbeb",
    },
    "beauty": {
        "label": "Beleza e cuidados pessoais",
        "icon": "scissors",
        "primary": "#be185d",
        "primary_dark": "#9d174d",
        "secondary": "#a21caf",
        "accent": "#f9a8d4",
        "hero": "#3b0a2e",
        "tint": "#fdf2f8",
    },
    "hardware": {
        "label": "Ferramentas e materiais",
        "icon": "tools",
        "primary": "#c2410c",
        "primary_dark": "#9a3412",
        "secondary": "#b45309",
        "accent": "#fbbf24",
        "hero": "#1c1917",
        "tint": "#fff7ed",
    },
}
CATEGORY_GROUPS = {
    "automotive": {
        "car_repair", "car_parts", "car", "car_wash", "tyres", "auto_parts",
        "autopecas", "oficina", "automotive",
    },
    "health": {
        "pharmacy", "clinic", "doctors", "dentist", "healthcare", "medical",
        "hospital", "laboratory", "optician", "veterinary", "farmacia", "clinica",
    },
    "restaurant": {"restaurant", "cafe", "bar", "fast_food", "food", "pub"},
    "bakery": {"bakery", "confectionery", "patisserie", "padaria"},
    "beauty": {"hairdresser", "beauty", "beauty_salon", "salon", "barber", "barbearia"},
    "hardware": {"hardware", "doityourself", "tool", "building_materials", "ferragens"},
}
CATEGORY_ICONS = {
    "store": '<svg aria-hidden="true" viewBox="0 0 24 24" class="h-5 w-5" fill="none"><path d="M4 10v10h16V10M3 10l2-6h14l2 6M3 10a3 3 0 0 0 6 0 3 3 0 0 0 6 0 3 3 0 0 0 6 0M9 20v-6h6v6" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "car": '<svg aria-hidden="true" viewBox="0 0 24 24" class="h-5 w-5" fill="none"><path d="m5 11 1.5-5h11L19 11l2 2v5h-2v-2H5v2H3v-5l2-2Zm1 0h12M7 16h.01M17 16h.01" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/><circle cx="7" cy="13.5" r="1" fill="currentColor"/><circle cx="17" cy="13.5" r="1" fill="currentColor"/></svg>',
    "medical": '<svg aria-hidden="true" viewBox="0 0 24 24" class="h-5 w-5" fill="none"><path d="M9 3h6v6h6v6h-6v6H9v-6H3V9h6V3Z" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>',
    "restaurant": '<svg aria-hidden="true" viewBox="0 0 24 24" class="h-5 w-5" fill="none"><path d="M4 3v7a3 3 0 0 0 6 0V3M7 3v18m10-18v18m0-18c-2 2-3 5-3 8h6c0-3-1-6-3-8Z" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "bakery": '<svg aria-hidden="true" viewBox="0 0 24 24" class="h-5 w-5" fill="none"><path d="M4 11a8 8 0 0 1 16 0v9H4v-9Zm4-2v3m4-4v4m4-3v3M4 15h16" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "scissors": '<svg aria-hidden="true" viewBox="0 0 24 24" class="h-5 w-5" fill="none"><circle cx="6" cy="6" r="3" stroke="currentColor" stroke-width="1.7"/><circle cx="6" cy="18" r="3" stroke="currentColor" stroke-width="1.7"/><path d="m8.2 7.8 12 12M8.2 16.2l12-12M13 12l7 7" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>',
    "tools": '<svg aria-hidden="true" viewBox="0 0 24 24" class="h-5 w-5" fill="none"><path d="M14 6a5 5 0 0 0-6.5 6.5L3 17l4 4 4.5-4.5A5 5 0 0 0 18 10l-3 3-4-4 3-3Z" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>',
}


def load_client(path: Path, csv_row: int = 1) -> dict[str, Any]:
    try:
        if path.suffix.lower() == ".csv":
            with path.open(encoding="utf-8-sig", newline="") as source:
                reader = csv.DictReader(source)
                if not reader.fieldnames:
                    raise ValueError("O CSV precisa ter uma linha de cabeçalho.")
                rows = list(reader)
            if csv_row < 1 or csv_row > len(rows):
                raise ValueError(f"Linha CSV inválida: escolha um número entre 1 e {len(rows)}.")
            row = {str(key).strip().lower(): value for key, value in rows[csv_row - 1].items() if key}
            client = {
                "nome_empresa": row.get("nome_empresa") or row.get("nome") or row.get("name"),
                "cidade": row.get("cidade") or row.get("city"),
                "categoria": row.get("categoria") or row.get("category") or row.get("shop") or row.get("amenity") or row.get("craft"),
                "whatsapp": row.get("whatsapp") or row.get("telefone") or row.get("phone"),
                "descricao": row.get("descricao") or row.get("description"),
                "slug": row.get("slug"),
            }
        else:
            with path.open(encoding="utf-8") as source:
                client = json.load(source)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Não foi possível ler os dados do cliente: {error}") from error
    if not isinstance(client, dict):
        raise ValueError("O arquivo JSON deve conter um objeto.")
    return client


def validate_client(client: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_FIELDS if not str(client.get(field, "")).strip()]
    if missing:
        raise ValueError("Campos obrigatórios ausentes: " + ", ".join(missing))


def normalize_category(value: Any) -> str:
    normalized = unicodedata.normalize("NFKD", str(value or "").strip().lower())
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    category = re.sub(r"[\s-]+", "_", normalized.split("=")[-1])
    for theme_name, categories in CATEGORY_GROUPS.items():
        if category in categories:
            return theme_name
    return "default"


def theme_for_category(value: Any) -> dict[str, str]:
    return CATEGORY_THEMES[normalize_category(value)]


def escape_text(value: Any) -> str:
    return html.escape(str(value).strip(), quote=True)


def normalize_whatsapp(value: Any) -> str:
    digits = re.sub(r"\D", "", str(value))
    if not 10 <= len(digits) <= 15:
        raise ValueError("WhatsApp deve incluir o código do país e ter de 10 a 15 dígitos.")
    return digits


def safe_slug(value: Any) -> str:
    slug = str(value or "").strip().lower()
    if not SLUG_PATTERN.fullmatch(slug):
        raise ValueError("O campo 'slug' deve conter apenas letras minúsculas, números e hífens.")
    return slug


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_name).strip("-")
    return safe_slug(slug)


def render_page(client: dict[str, Any]) -> str:
    try:
        template = TEMPLATE_PATH.read_text(encoding="utf-8")
    except OSError as error:
        raise ValueError(f"Não foi possível ler o template: {error}") from error

    whatsapp = normalize_whatsapp(client["whatsapp"])
    services = client.get("servicos", [])
    if not isinstance(services, list) or any(not isinstance(item, str) for item in services):
        raise ValueError("'servicos' deve ser uma lista de textos.")
    services_html = "\n".join(
        f'<li class="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft transition-all duration-300 hover:-translate-y-1.5 hover:shadow-xl" data-aos="fade-up" data-aos-delay="{100 + (index % 3) * 100}">{escape_text(service)}</li>'
        for index, service in enumerate(services)
        if service.strip()
    )
    if not services_html:
        services_html = '<li class="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft transition-all duration-300 hover:-translate-y-1.5 hover:shadow-xl" data-aos="fade-up" data-aos-delay="100">Atendimento personalizado</li>'

    category = client.get("categoria") or client.get("category") or client.get("shop") or ""
    theme = theme_for_category(category)

    replacements = {
        "{{NOME_EMPRESA}}": escape_text(client["nome_empresa"]),
        "{{CIDADE}}": escape_text(client["cidade"]),
        "{{WHATSAPP}}": escape_text(client["whatsapp"]),
        "{{WHATSAPP_LINK}}": f"https://wa.me/{whatsapp}",
        "{{DESCRICAO}}": escape_text(client["descricao"]),
        "{{SERVICOS_HTML}}": services_html,
        "{{ANO}}": str(__import__("datetime").datetime.now().year),
        "{{THEME_PRIMARY}}": theme["primary"],
        "{{THEME_PRIMARY_DARK}}": theme["primary_dark"],
        "{{THEME_SECONDARY}}": theme["secondary"],
        "{{THEME_ACCENT}}": theme["accent"],
        "{{THEME_HERO}}": theme["hero"],
        "{{THEME_TINT}}": theme["tint"],
        "{{ICONE_CATEGORIA}}": CATEGORY_ICONS[theme["icon"]],
        "{{ROTULO_CATEGORIA}}": escape_text(theme["label"]),
    }
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)
    if re.search(r"\{\{[A-Z_]+\}\}", template):
        raise ValueError("O template contém variáveis não preenchidas.")
    return template


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera uma landing page estática para um cliente.")
    parser.add_argument("cliente_json", type=Path, help="Arquivo JSON ou CSV com os dados do cliente.")
    parser.add_argument("--output", type=Path, default=Path("public"), help="Diretório de publicação.")
    parser.add_argument("--csv-row", type=int, default=1, help="Número do registro CSV, começando em 1.")
    parser.add_argument("--whatsapp", help="WhatsApp internacional para completar ou substituir o dado de origem.")
    parser.add_argument("--descricao", help="Descrição comercial para completar ou substituir o dado de origem.")
    args = parser.parse_args()

    try:
        client = load_client(args.cliente_json, args.csv_row)
        if args.whatsapp:
            client["whatsapp"] = args.whatsapp
        if args.descricao:
            client["descricao"] = args.descricao
        validate_client(client)
        slug = safe_slug(client["slug"]) if client.get("slug") else slugify(client["nome_empresa"])
        destination = args.output.resolve() / slug / "index.html"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(render_page(client), encoding="utf-8")
    except (OSError, ValueError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1
    print(f"Landing page gerada em: {destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())