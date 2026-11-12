"""Offline tests for actual parsing code; no Home Assistant stubs are used."""

from datetime import UTC, datetime
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("pogoda_parser", ROOT / "custom_components/pogoda_by/parser.py")
parser = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = parser
spec.loader.exec_module(parser)


def rss(description, date="Fri Oct 10 2025 08:00:00 GMT+0000 (Coordinated Universal Time)"):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0"><channel><item><pubDate>{date}</pubDate>
    <link>https://pogoda.by/observation/meteo-observation/26851</link>
    <description><![CDATA[{description}]]></description></item></channel></rss>"""


SAMPLE = "Температура +10.7°C | Давление 983.9 гПа, падает | Ветер 1.8 м/с, Западный | Погода: Без особых явлений "


class CatalogTests(unittest.TestCase):
    def test_array_uses_id_not_array_index(self):
        result = parser.normalize_catalog({"BY": [None, {"id": 26851, "name": "Минск-Независимости", "lat": "53.9", "lng": "27.5"}]})
        self.assertEqual(set(result["BY"]), {"26851"})
        self.assertEqual(result["BY"]["26851"].latitude, 53.9)

    def test_country_keyed_object(self):
        result = parser.normalize_catalog({"pl": {"5": {"id": "12372", "name": "Варшава", "icao": "EPWA", "timezone": "Europe/Warsaw"}}})
        self.assertEqual(result["PL"]["12372"].icao, "EPWA")
        self.assertEqual(result["PL"]["12372"].timezone, "Europe/Warsaw")

    def test_duplicate_names_remain_separate(self):
        result = parser.normalize_catalog({"PL": [{"id": 1, "name": "Варшава"}, {"id": 2, "name": "Варшава"}]})
        self.assertEqual(len(result["PL"]), 2)

    def test_invalid_and_missing_station_ids(self):
        records = [{"id": None, "name": "x"}, {"id": "../x", "name": "x"}, {"name": "x"}, {"id": 1}, {"id": 2, "name": " "}]
        with self.assertRaises(parser.InvalidData):
            parser.normalize_catalog({"BY": records})

    def test_malformed_rows_and_metadata_are_skipped(self):
        result = parser.normalize_catalog({"meta": 1, "BY": [None, "x", {"id": 1, "name": "x"}], "PL": None})
        self.assertEqual(set(result), {"BY"})

    def test_empty_or_invalid_top_level(self):
        for value in ({}, [], None, {"BY": []}, {"BY": "error"}):
            with self.subTest(value=value), self.assertRaises(parser.InvalidData):
                parser.normalize_catalog(value)

    def test_coordinates_zero_and_invalid(self):
        result = parser.normalize_catalog({"BY": [{"id": 1, "name": "x", "lat": 0, "lng": "0"}, {"id": 2, "name": "y", "lat": "NaN", "lng": 181}]})
        self.assertEqual(result["BY"]["1"].latitude, 0)
        self.assertEqual(result["BY"]["1"].longitude, 0)
        self.assertIsNone(result["BY"]["2"].latitude)
        self.assertIsNone(result["BY"]["2"].longitude)

    def test_round_trip_station_metadata(self):
        station = parser.Station("BY", "26851", "Минск", 53.9, 27.5)
        self.assertEqual(parser.Station(**station.as_dict()), station)


class RssTests(unittest.TestCase):
    def test_original_package_example(self):
        result = parser.parse_rss(rss(SAMPLE))
        self.assertEqual(result.values, {
            "temperature": 10.7, "pressure": 983.9, "pressure_trend": "падает",
            "wind_speed": 1.8, "wind_direction": "Западный", "condition": "Без особых явлений",
            "observation_time": datetime(2025, 10, 10, 8, tzinfo=UTC),
        })

    def test_negative_unicode_minus_and_comma_decimal(self):
        result = parser.parse_rss(rss("Температура −12,75°С | Ветер 0,25 м/с, Северо-западный"))
        self.assertEqual(result.values["temperature"], -12.75)
        self.assertEqual(result.values["wind_speed"], 0.25)
        self.assertEqual(result.values["wind_direction"], "Северо-западный")

    def test_missing_fields_do_not_become_zero(self):
        result = parser.parse_rss(rss("Температура -2°C"))
        self.assertNotIn("pressure", result.values)
        self.assertNotIn("wind_speed", result.values)

    def test_calm_is_valid_zero_wind(self):
        result = parser.parse_rss(rss("Ветер: штиль"))
        self.assertEqual(result.values["wind_speed"], 0)
        self.assertEqual(result.values["wind_direction"], "Штиль")

    def test_condition_preserves_commas_and_qualifiers(self):
        result = parser.parse_rss(rss("Погода: Дождь, слабый, в последний час"))
        self.assertEqual(result.values["condition"], "Дождь, слабый, в последний час")

    def test_html_and_nonbreaking_spaces(self):
        result = parser.parse_rss(rss("<b>Температура</b>&nbsp;+4.25°C | Ветер 2 м/с"))
        self.assertEqual(result.values["temperature"], 4.25)
        self.assertEqual(result.values["wind_speed"], 2)

    def test_optional_observations(self):
        result = parser.parse_rss(rss("Влажность 85% | Порывы до 12.5 м/с | Видимость 10 км"))
        self.assertEqual(result.values["humidity"], 85)
        self.assertEqual(result.values["wind_gust"], 12.5)
        self.assertEqual(result.values["visibility"], 10)

    def test_invalid_numeric_fields_omitted(self):
        result = parser.parse_rss(rss("Влажность 101% | Давление -2 гПа | Ветер -1 м/с | Температура 0°C"))
        self.assertNotIn("humidity", result.values)
        self.assertNotIn("pressure", result.values)
        self.assertNotIn("wind_speed", result.values)
        self.assertEqual(result.values["temperature"], 0)

    def test_bad_date_keeps_weather(self):
        result = parser.parse_rss(rss("Температура 0°C", "not a date"))
        self.assertNotIn("observation_time", result.values)

    def test_html_error_empty_feed_and_unrecognized_text_fail(self):
        for value in ("<html>Unavailable</html>", "<rss><channel /></rss>", rss(""), rss("Сервис недоступен"), "broken <xml"):
            with self.subTest(value=value), self.assertRaises(parser.InvalidData):
                parser.parse_rss(value)

    def test_xml_entities_rejected(self):
        value = '<!DOCTYPE rss [<!ENTITY x "hello">]><rss><channel /></rss>'
        with self.assertRaises(parser.InvalidData):
            parser.parse_rss(value)

    def test_namespaced_rss(self):
        value = rss(SAMPLE).replace('<rss version="2.0">', '<rss version="2.0" xmlns="urn:rss">')
        self.assertEqual(parser.parse_rss(value).values["temperature"], 10.7)

    def test_newest_item_selected(self):
        older = '<item><pubDate>Thu, 09 Oct 2025 08:00:00 +0000</pubDate><description>Температура 1°C</description></item>'
        value = rss(SAMPLE).replace("<channel>", f"<channel>{older}")
        self.assertEqual(parser.parse_rss(value).values["temperature"], 10.7)


class TimestampTests(unittest.TestCase):
    def test_js_date_with_offset(self):
        self.assertEqual(parser.parse_timestamp("Fri Oct 10 2025 11:00:00 GMT+0300 (Moscow Standard Time)"), datetime(2025, 10, 10, 8, tzinfo=UTC))

    def test_rfc_date(self):
        self.assertEqual(parser.parse_timestamp("Fri, 10 Oct 2025 08:00:00 +0000"), datetime(2025, 10, 10, 8, tzinfo=UTC))

    def test_iso_date(self):
        self.assertEqual(parser.parse_timestamp("2025-10-10T08:00:00Z"), datetime(2025, 10, 10, 8, tzinfo=UTC))

    def test_invalid_and_naive_dates(self):
        for value in (None, "", "invalid", "2025-10-10T08:00:00", "Fri Xxx 10 2025 08:00:00 GMT+0000", "Fri Oct 40 2025 08:00:00 GMT+0000"):
            with self.subTest(value=value):
                self.assertIsNone(parser.parse_timestamp(value))


if __name__ == "__main__":
    unittest.main()
