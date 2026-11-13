# Pogoda.by dla Home Assistant — 0.2.0

[Русский](README.ru.md) | [English](../README.md) | [Polski](README.pl.md) | [Беларуская](README.be.md) | [Deutsch](README.de.md)

Niestandardowa integracja Home Assistant. Pobiera aktualne obserwacje pogodowe z serwisu Belhydromet przez RSS, a listę krajów i stacji — przez API w formacie JSON. Klucz API nie jest wymagany. Integracja nie udostępnia prognozy pogody.

![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)
![Version](https://img.shields.io/badge/version-v0.2.0-blue.svg)

> ⚠️ **Ważna uwaga:** Integracja udostępnia pełne informacje dla stacji meteorologicznych **na Białorusi**. Dla stacji w innych krajach informacje są często **niedostępne lub niekompletne**, ponieważ usługa Pogoda.by jest zorientowana przede wszystkim na dane Belhydrometu (Białoruś). Jeśli wybrałeś stację z innego kraju i czujniki wykazują błąd lub stają się niedostępne, jest to spowodowane brakiem dostępu do danych z usługi Pogoda.by.

## Instalacja przez Marketplace / HACS

Integracja obsługuje instalację przez Marketplace / HACS z repozytorium `Toropyga/pogoda_by`.

[![Zainstaluj przez HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Toropyga&repository=pogoda_by&category=Integration)

### Home Assistant 2026.11 i nowszy — Marketplace

Od wersji **Home Assistant 2026.11** HACS jest wbudowany w Home Assistant pod nazwą **Marketplace**. Oddzielna instalacja HACS nie jest potrzebna. Administratorzy znajdą Marketplace w ustawieniach. Pogoda.by nie znajduje się jeszcze w domyślnym katalogu, dlatego dodaj repozytorium za pomocą odnośnika.

1. Otwórz **Ustawienia → Marketplace**.
2. Wybierz **Dodaj z linku / Add from link**.
3. Wpisz `https://github.com/Toropyga/pogoda_by` i kliknij **Dodaj / Add**.
4. Połącz konto GitHub, jeśli pojawi się taka prośba: połączenie jest wymagane dla repozytoriów niestandardowych. Jeśli typ nie zostanie rozpoznany automatycznie, wybierz **Integration**.
5. Otwórz **Pogoda.by** i wybierz **Zainstaluj / Install**.
6. Wybierz kraj i stację w formularzu konfiguracji. Jeśli Marketplace poprosi o ponowne uruchomienie, wykonaj je, a następnie przejdź do sekcji konfiguracji poniżej.

Pierwsza instalacja może od razu otworzyć konfigurację bez ponownego uruchamiania. Podczas aktualizacji istniejącej instalacji postępuj zgodnie z komunikatem Marketplace dotyczącym ponownego uruchomienia.

### Home Assistant 2026.10 i starszy — HACS

W starszych wersjach [HACS](https://www.hacs.xyz/) musi być wcześniej zainstalowany i skonfigurowany. Dodaj integrację jako repozytorium niestandardowe:

1. Otwórz **HACS** w Home Assistant.
2. Wybierz **⋮ → Repozytoria niestandardowe / Custom repositories**.
3. Wpisz adres `https://github.com/Toropyga/pogoda_by`.
4. Wybierz typ **Integracja / Integration** i kliknij **Dodaj / Add**.
5. Znajdź **Pogoda.by**, otwórz jej stronę i kliknij **Pobierz / Download**.
6. Potwierdź pobranie proponowanej wersji. Jeśli nie opublikowano jeszcze wydań, HACS korzysta z domyślnej gałęzi repozytorium.
7. Uruchom ponownie Home Assistant i wykonaj konfigurację opisaną poniżej.

Marketplace i HACS umieszczają pliki w `/config/custom_components/pogoda_by/`, razem z katalogami `frontend`, `brand` i `translations`. Kolejne opublikowane wersje można pobierać przez odpowiedni interfejs.

Jeśli integracja została zainstalowana ręcznie, dodaj to samo repozytorium do Marketplace lub HACS i zainstaluj ją, zastępując istniejące pliki. Zmiana sposobu instalacji nie wymaga usuwania wpisu Pogoda.by w sekcji „Urządzenia oraz usługi”.

## Instalacja ręczna

1. Skopiuj katalog `custom_components/pogoda_by` z tego projektu do katalogu konfiguracji Home Assistant. Docelowa ścieżka powinna mieć postać `/config/custom_components/pogoda_by/manifest.json`.
2. Uruchom ponownie Home Assistant.
3. Wykonaj konfigurację opisaną poniżej.

## Konfiguracja po instalacji

[![Dodaj integrację](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=pogoda_by)

1. Otwórz **Ustawienia → Urządzenia oraz usługi → Dodaj integrację → Pogoda.by**.
2. Wybierz kraj z katalogu, a następnie stację z listy dla tego kraju. Etykieta zawiera rzeczywisty identyfikator stacji, a nie jej pozycję w danych JSON.
3. Poczekaj na pierwszą poprawną odpowiedź RSS. Jeśli stacja nie udostępnia obsługiwanych danych pogodowych, formularz poinformuje o tym i umożliwi wybór innej stacji.

Aby korzystać z kilku stacji, dodaj integrację kilka razy. Ponowne dodanie tej samej stacji jest blokowane. Aby zmienić stację, dodaj nowy wpis i usuń poprzedni, gdy nie będzie już potrzebny.

Jest to wersja wstępna. Kod źródłowy: https://github.com/Toropyga/pogoda_by. W przypadku instalacji ręcznej pobierz repozytorium przez **Code → Download ZIP** i rozpakuj je. W katalogu `custom_components` umieść tylko zagnieżdżony katalog `pogoda_by`. Osobne wydanie GitHub Release nie jest wymagane do instalacji przez Marketplace / HACS. Przygotowanie publikacji opisano w pliku [HACS.md](HACS.md) w języku rosyjskim.

## Języki interfejsu

Obsługiwane są języki **białoruski (`be`), polski (`pl`), rosyjski (`ru`), angielski (`en`) i niemiecki (`de`)**. Przetłumaczono wybór kraju i stacji, komunikaty o błędach, ustawienia aktualizacji oraz nazwy sensorów.

Język jest wybierany automatycznie na podstawie języka interfejsu Home Assistant w profilu użytkownika. Osobny przełącznik języka w integracji nie jest potrzebny. Nazwy encji nadane przez użytkownika nie są nadpisywane.

Nazwy stacji i wartości tekstowe otrzymane z Pogoda.by są zachowywane w oryginalnej postaci. Na przykład opisy pogody, tendencja ciśnienia i kierunek wiatru z rosyjskojęzycznego kanału RSS nie są tłumaczone automatycznie; odczyty liczbowe są jednakowe we wszystkich językach.

## Ikona integracji

Integracja zawiera ikonę **Pogoda.by** z przezroczystym tłem:

- `custom_components/pogoda_by/brand/icon.png` — 256×256 pikseli;
- `custom_components/pogoda_by/brand/icon@2x.png` — 512×512 pikseli.

Home Assistant **2026.3 i nowszy** automatycznie korzysta z obrazów w katalogu `brand`. Dodatkowe ustawienia w `manifest.json` nie są potrzebne. Podczas aktualizacji zainstalowanej integracji skopiuj cały katalog `pogoda_by`, uruchom ponownie Home Assistant i odśwież stronę w przeglądarce. Starsze wersje Home Assistant nie obsługują w ten sposób lokalnych obrazów integracji.

Obraz źródłowy zapisano jako `assets/pogoda-by-source.png`. Aby ponownie przygotować wymagane rozmiary w systemie Windows, uruchom `./tools/build_brand.ps1` z katalogu projektu.

## Karta na pulpicie

**Pogoda.by Card 0.2.0** jest instalowana i aktualizowana razem z integracją. Podczas instalacji ręcznej skopiuj cały katalog `custom_components/pogoda_by`, łącznie z `frontend`, `brand` i `translations`. Nie jest potrzebne drugie repozytorium karty ani osobne kopiowanie JavaScript do `/config/www`.

Po instalacji lub aktualizacji uruchom ponownie Home Assistant i odśwież przeglądarkę. W edytorze pulpitu wybierz **Dodaj kartę → Pogoda.by Card**, a następnie skonfigurowaną stację. Użytkownik sam umieszcza kartę na wybranym pulpicie; zasób JavaScript jest rejestrowany automatycznie przy standardowym zarządzaniu zasobami w interfejsie.

Karta wyświetla temperaturę, opis pogody, wiatr, ciśnienie i czas obserwacji. Oznacza nieaktualne dane, obsługuje widok kompaktowy, jasny i ciemny motyw oraz pięć języków. Wilgotność, porywy i widoczność pojawiają się tylko wtedy, gdy dane są dostępne. Kliknięcie odczytu otwiera szczegóły encji. Opcjonalny wykres temperatury korzysta z Recorder/History Home Assistant; karta nie tworzy prognozy.

Przykład konfiguracji — zastąp `BY_26850` własną stacją lub wybierz ją w edytorze wizualnym:

```yaml
type: custom:pogoda-by-card
station: BY_26850
show_details: true
show_graph: true
hours_to_show: 24
stale_after: 180
compact: false
language: auto
```

Przy **zasobach zarządzanych w YAML** (`lovelace.resource_mode: yaml`) dodaj `/pogoda_by/pogoda-by-card.js?v=0.2.0` z `type: module` do istniejącej listy zasobów, przeładuj zasoby i odśwież przeglądarkę. Pulpit YAML może korzystać z zasobów zarządzanych w interfejsie; o automatycznej rejestracji decyduje tryb zarządzania zasobami.

Aktualizacja zachowuje skonfigurowane stacje i zmienia URL zasobu karty. W trybie storage poprzedni ręczny wpis `/local/pogoda-by-card.js` jest przenoszony automatycznie, a duplikaty znanych lokalnych adresów karty są scalane. Zmienione identyfikatory entity_id sensorów są obsługiwane.

[Instrukcja karty po angielsku](CARD.md), [instrukcja po rosyjsku](CARD.ru.md), [historia zmian](../CHANGELOG.md).

## Sensory

Sensor jest tworzony, gdy odpowiadające mu pole pojawi się po raz pierwszy w RSS. Jeśli pole pojawi się później, ponowne uruchomienie nie jest potrzebne. Jeśli wcześniej dostępne pole zniknie, sensor stanie się niedostępny; brakujących odczytów nie zastępuje się zerem.

| Pole | Jednostka / typ | Dodatkowe informacje |
| --- | --- | --- |
| Temperatura | °C | Obsługa wartości ujemnych oraz kropki lub przecinka dziesiętnego |
| Ciśnienie atmosferyczne | hPa | Atrybut `status`: tendencja z RSS |
| Tendencja ciśnienia | Tekst | Na przykład „spada” |
| Prędkość wiatru | m/s | `direction` i `speed_kmh`; jednostki można zmienić w Home Assistant |
| Kierunek wiatru | Tekst | Cisza nie jest przedstawiana jako wiatr północny |
| Pogoda | Tekst | Pełny opis i oryginalny tekst w atrybutach |
| Czas obserwacji | Znacznik czasu | `pubDate` przeliczony na UTC; interfejs wyświetla czas lokalny |
| Stacja meteorologiczna | Tekst diagnostyczny | ID, kraj, nazwa, współrzędne, strefa czasowa, ICAO i odnośnik |
| Wilgotność | % | Tylko jeśli RSS zawiera to pole wprost |
| Porywy wiatru | m/s | Tylko jeśli RSS zawiera to pole wprost |
| Widoczność | km | Tylko jeśli RSS zawiera to pole w kilometrach |

Parser obsługuje wilgotność, porywy wiatru i widoczność jako pola opcjonalne, ale ich dostępność w obecnej usłudze nie została potwierdzona. Integracja nie oblicza ich na podstawie innych odczytów.

Każda stacja jest reprezentowana przez osobne urządzenie. Encje mają stałe identyfikatory unique_id oparte na kraju, ID stacji i rodzaju pomiaru. Identyfikatory entity_id nadaje Home Assistant.

Domyślny interwał aktualizacji wynosi **1 godzinę (60 minut)**. Przycisk **Konfiguruj** przy wpisie integracji pozwala wybrać od 5 do 180 minut. W każdym cyklu wykonywane jest jedno zapytanie RSS dla wszystkich sensorów danej stacji. Katalog jest pobierany podczas konfiguracji; metadane wybranej stacji są zapisywane we wpisie i nie wymagają ponownego pobierania przy uruchamianiu Home Assistant.

Po aktualizacji wartość domyślna jest stosowana do wpisów bez zapisanego interwału. Jeśli interwał zapisano przez **Konfiguruj**, pozostaje on bez zmian; aby ustawić aktualizację co godzinę, wpisz ręcznie **60**.

W przypadku błędu HTTP, przekroczenia limitu czasu lub nieprawidłowej odpowiedzi RSS sensory pogodowe stają się niedostępne. Home Assistant automatycznie ponawia aktualizację. Diagnostyczny sensor stacji przechowuje metadane lokalnie i pozostaje dostępny. Poprawna odpowiedź ze starą datą obserwacji nie jest traktowana jako błąd sieciowy: sprawdzaj czas obserwacji. Integracja nie gwarantuje, że sama stacja publikuje nowe pomiary co godzinę.

Encja `weather` z prognozą nie jest tworzona. Obserwacje można wyświetlać w Pogoda.by Card lub standardowych kartach encji, kafelkach i wykresach sensorów. Odczyty liczbowe mają device_class, state_class i standardowe jednostki Home Assistant.

## Weryfikacja

Testy parsowania JSON/RSS działające bez dostępu do sieci korzystają ze standardowej biblioteki Pythona:

```powershell
python -m unittest discover -s tests -v
node --check custom_components/pogoda_by/frontend/pogoda-by-card.js
node --test tests/test_card.cjs
```

Sprawdzenie bieżących odpowiedzi serwisu bez instalowania Home Assistant:

```powershell
python tools/check_live.py --country BY --station 26851
python tools/check_live.py --country PL --station 12372
```

Skrypt jedynie odczytuje dane publiczne. Nie zmienia konfiguracji Home Assistant. Aby zdiagnozować komunikaty integracji, można tymczasowo włączyć:

```yaml
logger:
  logs:
    custom_components.pogoda_by: debug
```

## Stan weryfikacji tej wersji

Dla wersji 0.2.0 lokalnie przeszło **50 testów Pythona i 18 testów logiki karty**, a także kontrole składni, spójności kluczy tłumaczeń i białych znaków. Testy karty używają minimalnego modelu DOM, a testy rejestracji — atrap API Home Assistant; nie potwierdzają działania w rzeczywistym interfejsie Home Assistant.

Rzeczywiste odpowiedzi API/RSS, rejestracja zasobu, wykres danych Recorder i wygląd na komputerze oraz telefonie wymagają jeszcze sprawdzenia. Szczegóły po rosyjsku: [stan weryfikacji](../VALIDATION.md). Docelowa minimalna wersja to Home Assistant 2025.1; zgodność podczas rzeczywistego uruchomienia nie została jeszcze potwierdzona.

## Źródła

- Marketplace: https://www.home-assistant.io/integrations/marketplace/
- Przejście z HACS: https://contributors.home-assistant.io/marketplace/how-it-works/
- Katalog: https://pogoda.by/api/v2/weather-fact/all-cities
- RSS: https://pogoda.by/rss/weather?station=26851
- Dokumentacja Home Assistant: https://contributors.home-assistant.io/core/integrations/config-entries/
- Pobieranie danych: https://contributors.home-assistant.io/core/integrations/fetching-data/

Dane udostępnia Belhydromet. Projekt nie jest oficjalną integracją tej instytucji.
