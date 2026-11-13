# Pogoda.by für Home Assistant — 0.1.4

[Русский](README.ru.md) | [English](../README.md) | [Polski](README.pl.md) | [Беларуская](README.be.md) | [Deutsch](README.de.md)

Eine benutzerdefinierte Integration für Home Assistant. Sie ruft die aktuelle Wetterbeobachtung von Belhydromet per RSS ab; die Liste der Länder und Stationen stammt aus einer JSON-API. Es ist kein API-Schlüssel erforderlich. Wettervorhersagen werden nicht bereitgestellt.

![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)
![Version](https://img.shields.io/badge/version-v0.1.4-blue.svg)

> ⚠️ **Wichtiger Hinweis:** Die Integration liefert vollständige Informationen für Wetterstationen **in Belarus**. Für Stationen in anderen Ländern sind die Informationen oft **nicht verfügbar oder unvollständig**, da der Dienst Pogoda.by in erster Linie auf Daten von Belhydromet (Belarus) ausgerichtet ist. Wenn Sie eine Station aus einem anderen Land ausgewählt haben und die Sensoren einen Fehler anzeigen oder nicht verfügbar werden, liegt dies an der fehlenden Datenverfügbarkeit beim Dienst Pogoda.by.

## Installation über Marketplace / HACS

Die Integration unterstützt die Installation über Marketplace / HACS aus dem Repository `Toropyga/pogoda_by`.

[![Installation über HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Toropyga&repository=pogoda_by&category=Integration)

### Home Assistant 2026.11 und neuer — Marketplace

Ab **Home Assistant 2026.11** ist HACS als **Marketplace** direkt in Home Assistant integriert. Eine separate HACS-Installation ist nicht erforderlich. Administratoren finden den Marketplace unter den Einstellungen. Pogoda.by befindet sich noch nicht im Standardkatalog, daher fügen Sie das Repository über einen Link hinzu.

1. Öffnen Sie **Einstellungen → Marketplace**.
2. Wählen Sie **Von Link hinzufügen / Add from link**.
3. Geben Sie `https://github.com/Toropyga/pogoda_by` ein und wählen Sie **Hinzufügen / Add**.
4. Verbinden Sie GitHub, falls dazu aufgefordert wird: Für benutzerdefinierte Repositorys ist eine Verbindung erforderlich. Wenn der Inhaltstyp nicht automatisch erkannt wird, wählen Sie **Integration**.
5. Öffnen Sie **Pogoda.by** und wählen Sie **Installieren / Install**.
6. Wählen Sie im Konfigurationsdialog ein Land und eine Station aus. Falls der Marketplace einen Neustart anfordert, führen Sie ihn zuerst aus und folgen Sie dann dem Abschnitt zur Konfiguration weiter unten.

Bei der ersten Installation öffnet sich die Konfiguration möglicherweise sofort ohne Neustart. Beim Aktualisieren einer bestehenden Installation folgen Sie der Benachrichtigung des Marketplace zum Neustart.

### Home Assistant 2026.10 und älter — HACS

In älteren Versionen muss [HACS](https://www.hacs.xyz/) bereits installiert und eingerichtet sein. Fügen Sie die Integration als benutzerdefiniertes Repository hinzu:

1. Öffnen Sie **HACS** in Home Assistant.
2. Wählen Sie **⋮ → Benutzerdefinierte Repositorys / Custom repositories**.
3. Geben Sie die Adresse `https://github.com/Toropyga/pogoda_by` ein.
4. Wählen Sie den Typ **Integration** und klicken Sie auf **Hinzufügen / Add**.
5. Suchen Sie **Pogoda.by**, öffnen Sie den Eintrag und klicken Sie auf **Herunterladen / Download**.
6. Bestätigen Sie die vorgeschlagene Version. Wenn noch keine Releases veröffentlicht wurden, verwendet HACS den Standardbranch des Repositorys.
7. Starten Sie Home Assistant neu und folgen Sie den Konfigurationsschritten weiter unten.

Marketplace und HACS legen die Dateien in `/config/custom_components/pogoda_by/` ab, einschließlich der Übersetzungen und des Ordners `brand`. Künftig veröffentlichte Versionen können über die jeweilige Oberfläche heruntergeladen werden.

Wenn die Integration bereits manuell installiert wurde, fügen Sie dasselbe Repository zu Marketplace oder HACS hinzu und installieren Sie es über die vorhandenen Dateien. Der Eintrag Pogoda.by unter „Geräte & Dienste“ muss beim Wechsel der Installationsmethode nicht gelöscht werden.

## Manuelle Installation

1. Kopieren Sie den Ordner `custom_components/pogoda_by` aus diesem Projekt in das Konfigurationsverzeichnis von Home Assistant. Der resultierende Pfad muss `/config/custom_components/pogoda_by/manifest.json` lauten.
2. Starten Sie Home Assistant neu.
3. Folgen Sie den Konfigurationsschritten weiter unten.

## Konfiguration nach der Installation

[![Integration hinzufügen](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=pogoda_by)

1. Öffnen Sie **Einstellungen → Geräte & Dienste → Integration hinzufügen → Pogoda.by**.
2. Wählen Sie ein Land aus dem Katalog und anschließend eine Station aus der Liste dieses Landes. Die Beschriftung enthält die tatsächliche Stations-ID und nicht ihre Position in den JSON-Daten.
3. Warten Sie auf die erste erfolgreiche RSS-Antwort. Wenn die Station keine unterstützten Wetterdaten veröffentlicht, meldet das Formular dies und lässt Sie eine andere Station auswählen.

Um mehrere Stationen zu verwenden, fügen Sie die Integration mehrfach hinzu. Das erneute Hinzufügen derselben Station wird blockiert. Um eine Station zu wechseln, fügen Sie einen neuen Eintrag hinzu und entfernen Sie den alten, sobald er nicht mehr benötigt wird.

Dies ist eine Vorabversion. Quellcode: https://github.com/Toropyga/pogoda_by. Laden Sie für die manuelle Installation das Repository über **Code → Download ZIP** herunter und entpacken Sie es. In `custom_components` gehört nur der verschachtelte Ordner `pogoda_by`. Für die Installation über Marketplace / HACS ist kein separates GitHub-Release erforderlich. Die Vorbereitung der Veröffentlichung ist in [HACS.md](../HACS.md) (auf Russisch) beschrieben.

## Oberflächensprachen

Unterstützt werden **Belarussisch (`be`), Polnisch (`pl`), Russisch (`ru`), Englisch (`en`) und Deutsch (`de`)**. Übersetzt sind die Auswahl von Land und Station, Fehlermeldungen, Aktualisierungseinstellungen und Sensornamen.

Die Sprache richtet sich automatisch nach der im Home-Assistant-Benutzerprofil ausgewählten Oberflächensprache. Ein separater Sprachumschalter in der Integration ist nicht erforderlich. Benutzerdefinierte Entitätsnamen werden nicht überschrieben.

Stationsnamen und Textwerte, die von Pogoda.by empfangen werden, bleiben im Originalzustand erhalten. So werden beispielsweise Wetterbeschreibungen, Drucktendenz und Windrichtung aus dem russischsprachigen RSS-Feed nicht automatisch übersetzt; numerische Messwerte sind in jeder Sprache identisch.

## Integrationssymbol

Die Integration enthält ein **Pogoda.by**-Symbol mit transparentem Hintergrund:

- `custom_components/pogoda_by/brand/icon.png` — 256×256 Pixel;
- `custom_components/pogoda_by/brand/icon@2x.png` — 512×512 Pixel.

Home Assistant **2026.3 und neuer** verwendet die Bilder aus dem Ordner `brand` automatisch. Zusätzliche Einstellungen in `manifest.json` sind nicht erforderlich. Kopieren Sie beim Aktualisieren einer installierten Integration den gesamten Ordner `pogoda_by`, starten Sie Home Assistant neu und aktualisieren Sie die Browserseite. Ältere Home-Assistant-Versionen unterstützen lokale Integrationsbilder auf diese Weise nicht.

Das Quellbild ist unter `assets/pogoda-by-source.png` gespeichert. Um die benötigten Größen unter Windows neu zu erzeugen, führen Sie `./tools/build_brand.ps1` aus dem Projektverzeichnis aus.

## Sensoren

Ein Sensor wird erstellt, sobald das zugehörige Feld erstmals im RSS-Feed erscheint. Erscheint ein Feld später, ist kein Neustart erforderlich. Verschwindet ein zuvor verfügbares Feld, wird der Sensor nicht verfügbar; fehlende Messwerte werden nicht durch null ersetzt.

| Feld | Einheit / Typ | Zusätzliche Hinweise |
| --- | --- | --- |
| Temperatur | °C | Negative Werte sowie Dezimalpunkt oder -komma werden unterstützt |
| Luftdruck | hPa | Attribut `status`: Tendenz aus dem RSS-Feed |
| Drucktendenz | Text | Zum Beispiel „fallend“ |
| Windgeschwindigkeit | m/s | `direction` und `speed_kmh`; Einheiten können in Home Assistant geändert werden |
| Windrichtung | Text | Windstille wird nicht als Nordwind dargestellt |
| Wetter | Text | Vollständige Beschreibung und Originaltext in den Attributen |
| Beobachtungszeit | Zeitstempel | `pubDate`, in UTC umgerechnet; die Oberfläche zeigt die Ortszeit an |
| Wetterstation | Diagnosetext | ID, Land, Name, Koordinaten, Zeitzone, ICAO und Link |
| Luftfeuchtigkeit | % | Nur wenn der RSS-Feed dieses Feld ausdrücklich enthält |
| Windböen | m/s | Nur wenn der RSS-Feed dieses Feld ausdrücklich enthält |
| Sichtweite | km | Nur wenn der RSS-Feed dieses Feld ausdrücklich in Kilometern enthält |

Luftfeuchtigkeit, Windböen und Sichtweite sind im Parser als optionale Felder vorgesehen, ihre Verfügbarkeit im aktuellen Dienst ist jedoch nicht bestätigt. Die Integration leitet sie nicht aus anderen Messwerten ab.

Jede Station wird durch ein eigenes Gerät dargestellt. Entitäten haben stabile unique_id-Werte, die auf Land, Stations-ID und Messwerttyp basieren. Die entity_id-Werte vergibt Home Assistant.

Das Standard-Aktualisierungsintervall beträgt **1 Stunde (60 Minuten)**. Über **Konfigurieren** am Integrationseintrag lässt sich ein Intervall von 5 bis 180 Minuten wählen. Pro Zyklus wird eine RSS-Anfrage für alle Sensoren einer Station durchgeführt. Der Katalog wird während der Konfiguration geladen; die Metadaten der gewählten Station werden im Eintrag gespeichert und müssen beim Start von Home Assistant nicht erneut heruntergeladen werden.

Nach einem Update gilt der Standardwert für Einträge ohne explizit gespeichertes Intervall. Wurde ein Intervall über **Konfigurieren** gespeichert, bleibt es erhalten; setzen Sie es für eine stündliche Aktualisierung manuell auf **60**.

Bei einem HTTP-Fehler, einem Timeout oder einer ungültigen RSS-Antwort werden die Wettersensoren nicht verfügbar. Home Assistant wiederholt die Aktualisierung automatisch. Der Diagnosesensor der Station speichert Metadaten lokal und bleibt verfügbar. Eine erfolgreiche Antwort mit einem veralteten Beobachtungsdatum gilt nicht als Netzwerkfehler: Prüfen Sie die Beobachtungszeit. Die Integration garantiert nicht, dass die Station selbst stündlich neue Messungen veröffentlicht.

Es wird keine `weather`-Entität mit Vorhersage erstellt; verwenden Sie für die Anzeige Entitätskarten, Kacheln und Sensordiagramme. Numerische Messwerte besitzen device_class, state_class und die Standardeinheiten von Home Assistant.

## Überprüfung

Offline-Tests für das Parsen von JSON/RSS verwenden die Python-Standardbibliothek:

```powershell
python -m unittest discover -s tests -v
```

Überprüfung der aktuellen Antworten der Website ohne Installation von Home Assistant:

```powershell
python tools/check_live.py --country BY --station 26851
python tools/check_live.py --country PL --station 12372
```

Das Skript liest nur öffentlich zugängliche Daten. Es ändert die Home-Assistant-Konfiguration nicht. Zur Diagnose von Meldungen der Integration können Sie vorübergehend aktivieren:

```yaml
logger:
  logs:
    custom_components.pogoda_by: debug
```

## Prüfstatus dieser Version

Syntaxprüfungen, Konsistenzprüfungen der Übersetzungen und Offline-Tests werden lokal durchgeführt; die Ergebnisse sind in `VALIDATION.md` (auf Russisch) dokumentiert. In der Entwicklungsumgebung ist keine Test-Installation von Home Assistant vorhanden. Direkter Zugriff auf die API/RSS ist dort nicht möglich, sodass die tatsächlichen Antworten des Anbieters und der vollständige Installationsvorgang in einem laufenden Home Assistant noch überprüft werden müssen. Der Katalog-Parser unterstützt die Strukturen „Land → Stations-Array“ und „Land → Stations-Objekt“. Nicht unterstützte Änderungen am API-Schema führen zu einer Fehlermeldung statt zu erfundenen Daten.

Die Integration verwendet die Standard-APIs ConfigFlow, OptionsFlow, DataUpdateCoordinator und SensorEntity. Die angestrebte Mindestversion ist Home Assistant 2025.1; die tatsächliche Kompatibilität wurde noch nicht durch einen Lauf innerhalb von Home Assistant bestätigt.

## Quellen

- Marketplace: https://www.home-assistant.io/integrations/marketplace/
- Wechsel von HACS: https://contributors.home-assistant.io/marketplace/how-it-works/
- Katalog: https://pogoda.by/api/v2/weather-fact/all-cities
- RSS: https://pogoda.by/rss/weather?station=26851
- Home-Assistant-Dokumentation: https://contributors.home-assistant.io/core/integrations/config-entries/
- Datenabruf: https://contributors.home-assistant.io/core/integrations/fetching-data/

Die Daten werden von Belhydromet bereitgestellt. Das Projekt ist keine offizielle Integration von Belhydromet.
