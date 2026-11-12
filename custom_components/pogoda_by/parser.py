"""Parse the station catalogue and RSS observations without Home Assistant."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from html import unescape
import math
import re
from typing import Any
from xml.etree import ElementTree as ET


class InvalidData(ValueError):
    """The upstream response has an unsupported or empty structure."""


@dataclass(frozen=True)
class Station:
    """Stable station identity; array indices are never station IDs."""

    country: str
    station_id: str
    name: str
    latitude: float | None = None
    longitude: float | None = None
    timezone: str | None = None
    icao: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Observation:
    """Parsed observation, with absent fields kept absent instead of zero."""

    values: dict[str, Any]
    description: str
    published: str | None
    link: str | None


def _coordinate(value: Any, limit: int) -> float | None:
    try:
        number = float(str(value).replace(",", "."))
    except (ValueError, TypeError):
        return None
    return number if math.isfinite(number) and abs(number) <= limit else None


def normalize_catalog(payload: Any) -> dict[str, dict[str, Station]]:
    """Accept country -> array or country -> keyed object, preserving IDs."""
    if not isinstance(payload, dict):
        raise InvalidData("Expected a country-keyed JSON object")
    catalog: dict[str, dict[str, Station]] = {}
    for code, records in payload.items():
        if not isinstance(code, str) or not re.fullmatch(r"[A-Za-z]{2}", code):
            continue
        if isinstance(records, dict):
            records = list(records.values())
        if not isinstance(records, list):
            continue
        country = code.upper()
        stations = catalog.setdefault(country, {})
        for record in records:
            if not isinstance(record, dict):
                continue
            station_id = str(record.get("id", "")).strip()
            name = record.get("name")
            if not re.fullmatch(r"[0-9]+", station_id) or not isinstance(name, str) or not name.strip():
                continue
            stations[station_id] = Station(
                country=country,
                station_id=station_id,
                name=name.strip(),
                latitude=_coordinate(record.get("lat"), 90),
                longitude=_coordinate(record.get("lng"), 180),
                timezone=str(record["timezone"]) if record.get("timezone") else None,
                icao=str(record["icao"]) if record.get("icao") else None,
            )
    catalog = {code: rows for code, rows in catalog.items() if rows}
    if not catalog:
        raise InvalidData("No stations in the catalogue")
    return catalog


def parse_timestamp(value: str | None) -> datetime | None:
    """Parse RSS/RFC dates, JavaScript Date.toString(), or aware ISO dates."""
    if not value:
        return None
    value = re.sub(r"\s*\([^)]*\)\s*$", "", value.strip())
    # JS example: Fri Oct 10 2025 08:00:00 GMT+0000.
    match = re.fullmatch(
        r"[A-Za-z]{3}\s+([A-Za-z]{3})\s+(\d{1,2})\s+(\d{4})\s+"
        r"(\d{2}:\d{2}:\d{2})\s+GMT([+-]\d{4})", value
    )
    if match:
        months = {month: index for index, month in enumerate(
            ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"), 1
        )}
        month, day, year, clock, offset = match.groups()
        if month not in months:
            return None
        value = f"{year}-{months[month]:02d}-{int(day):02d}T{clock}{offset}"
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            result = parsedate_to_datetime(value)
        except (ValueError, TypeError, OverflowError):
            return None
    # Do not guess whether a date without an offset uses UTC or station time.
    return result.astimezone(UTC) if result.tzinfo is not None else None


def _text(value: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]*>", " ", value)).replace("\u2212", "-").split())


def _child_text(element: ET.Element, name: str) -> str | None:
    for child in element:
        if child.tag.rsplit("}", 1)[-1] == name:
            return "".join(child.itertext()).strip() or None
    return None


def parse_rss(xml: str) -> Observation:
    """Read a current observation; HTML errors and empty feeds are failures."""
    if re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b", xml, re.IGNORECASE):
        raise InvalidData("DTD and entities are not accepted")
    try:
        root = ET.fromstring(xml)
    except (ET.ParseError, ValueError) as err:
        raise InvalidData("Invalid RSS XML") from err
    items = [node for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "item"]
    if not items:
        raise InvalidData("RSS contains no observations")
    # Most feeds contain one item. Choose the newest dated item if several exist.
    oldest = datetime.min.replace(tzinfo=UTC)
    item = max(items, key=lambda node: parse_timestamp(_child_text(node, "pubDate")) or oldest)
    description = _text(_child_text(item, "description") or "")
    if not description:
        raise InvalidData("Empty observation description")
    values: dict[str, Any] = {}
    number = r"([+-]?\d+(?:[.,]\d+)?)"
    patterns = {
        "temperature": rf"Температура\s*:?\s*{number}\s*°?\s*[CС]",
        "pressure": rf"Давление\s*:?\s*{number}\s*(?:гПа|hPa)",
        "wind_speed": rf"Ветер\s*:?\s*{number}\s*м\s*/\s*с",
        "humidity": rf"(?:Относительная\s+)?Влажность\s*:?\s*{number}\s*%",
        "wind_gust": rf"[Пп]орыв\w*\s*(?:ветра\s*)?(?:до\s*)?:?\s*{number}\s*м\s*/\s*с",
        "visibility": rf"Видимость\s*:?\s*{number}\s*км",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            value = float(match[1].replace(",", "."))
            if not math.isfinite(value):
                continue
            if key == "humidity" and not 0 <= value <= 100:
                continue
            if key in ("pressure", "wind_speed", "wind_gust", "visibility") and value < 0:
                continue
            values[key] = value
    for section in description.split("|"):
        section = section.strip()
        if re.match(r"Давление\b", section, re.IGNORECASE):
            match = re.search(r"(?:гПа|hPa)\s*,\s*(.+)", section, re.IGNORECASE)
            if match:
                values["pressure_trend"] = match[1].strip()
        elif re.match(r"Ветер\b", section, re.IGNORECASE):
            match = re.search(r"м\s*/\s*с\s*,\s*(.+)", section, re.IGNORECASE)
            if match:
                values["wind_direction"] = match[1].strip()
            elif re.search(r"штиль", section, re.IGNORECASE):
                values["wind_speed"] = 0.0
                values["wind_direction"] = "Штиль"
        elif re.match(r"Погода\s*:", section, re.IGNORECASE):
            condition = section.split(":", 1)[1].strip()
            if condition:
                # Preserve the whole description, including commas and qualifiers.
                values["condition"] = condition
    if not values:
        raise InvalidData("RSS does not contain supported weather fields")
    published = _child_text(item, "pubDate")
    if (timestamp := parse_timestamp(published)) is not None:
        values["observation_time"] = timestamp
    link = _child_text(item, "link")
    return Observation(values, description, published, link)
