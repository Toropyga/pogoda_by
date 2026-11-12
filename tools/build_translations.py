"""Generate matching English, Russian, Belarusian and Polish UI strings."""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "custom_components/pogoda_by"
KEYS = ["temperature", "pressure", "pressure_trend", "wind_speed", "wind_direction", "condition", "observation_time", "station", "humidity", "wind_gust", "visibility"]


def translation(title_user, description_user, country, title_station, description_station, station,
                errors, duplicate, options_title, options_description, interval, sensors):
    return {
        "title": "Pogoda.by",
        "config": {
            "step": {
                "user": {"title": title_user, "description": description_user, "data": {"country": country}},
                "station": {"title": title_station, "description": description_station, "data": {"station_id": station}},
            },
            "error": dict(zip(["cannot_connect", "invalid_data", "no_weather", "invalid_country", "invalid_station"], errors)),
            "abort": {"already_configured": duplicate},
        },
        "options": {
            "step": {"init": {"title": options_title, "description": options_description, "data": {"update_interval": interval}}},
        },
        "entity": {"sensor": {key: {"name": name} for key, name in zip(KEYS, sensors, strict=True)}},
    }


TRANSLATIONS = {
    "en": translation(
        "Select a country", "Choose a country from the live Pogoda.by catalogue. If loading fails, submit again to retry.", "Country",
        "Select a weather station", "Select a station in {country}. The number in brackets is the station ID.", "Weather station",
        ["Unable to connect to Pogoda.by. Please try again.", "The station catalogue has an unsupported format or is empty.", "No supported weather data is currently available for this station. Try again or select another station.", "Select a country from the list.", "Select a station from the list."],
        "This station has already been added.", "Polling settings", "Fetch one RSS response per station at this interval. The provider may update observations less frequently.", "Update interval (minutes)",
        ["Temperature", "Atmospheric pressure", "Pressure trend", "Wind speed", "Wind direction", "Weather", "Observation time", "Station", "Humidity", "Wind gust", "Visibility"],
    ),
    "ru": translation(
        "Выберите страну", "Выберите страну из справочника Pogoda.by. При ошибке загрузки нажмите кнопку отправки ещё раз для повтора.", "Страна",
        "Выберите метеостанцию", "Выберите станцию в стране {country}. В квадратных скобках указан ID станции.", "Метеостанция",
        ["Не удалось подключиться к Pogoda.by. Повторите попытку.", "Справочник станций пуст или имеет неподдерживаемый формат.", "Станция сейчас не возвращает поддерживаемую погоду. Повторите попытку или выберите другую станцию.", "Выберите страну из списка.", "Выберите станцию из списка."],
        "Эта метеостанция уже добавлена.", "Настройки обновления", "С этим интервалом выполняется один RSS-запрос на станцию. Сама станция может публиковать наблюдения реже.", "Интервал обновления (минуты)",
        ["Температура", "Атмосферное давление", "Тенденция давления", "Скорость ветра", "Направление ветра", "Погода", "Время наблюдения", "Метеостанция", "Влажность", "Порывы ветра", "Видимость"],
    ),
    "be": translation(
        "Выберыце краіну", "Выберыце краіну з даведніка Pogoda.by. Калі не ўдалося загрузіць даведнік, адпраўце форму яшчэ раз.", "Краіна",
        "Выберыце метэастанцыю", "Выберыце станцыю ў краіне {country}. У квадратных дужках пазначаны ідэнтыфікатар станцыі.", "Метэастанцыя",
        ["Не ўдалося злучыцца з Pogoda.by. Паўтарыце спробу.", "Даведнік станцый пусты або мае фармат, які не падтрымліваецца.", "Станцыя зараз не вяртае падтрымліваныя даныя пра надвор'е. Паўтарыце спробу або выберыце іншую станцыю.", "Выберыце краіну са спіса.", "Выберыце станцыю са спіса."],
        "Гэтая метэастанцыя ўжо дададзена.", "Налады абнаўлення", "З гэтым інтэрвалам выконваецца адзін RSS-запыт для кожнай станцыі. Сама станцыя можа публікаваць назіранні радзей.", "Інтэрвал абнаўлення (хвіліны)",
        ["Тэмпература", "Атмасферны ціск", "Тэндэнцыя ціску", "Хуткасць ветру", "Напрамак ветру", "Надвор'е", "Час назірання", "Метэастанцыя", "Вільготнасць", "Парывы ветру", "Бачнасць"],
    ),
    "pl": translation(
        "Wybierz kraj", "Wybierz kraj z katalogu Pogoda.by. Jeśli pobieranie się nie powiedzie, wyślij formularz ponownie.", "Kraj",
        "Wybierz stację meteorologiczną", "Wybierz stację w kraju {country}. W nawiasach kwadratowych podano identyfikator stacji.", "Stacja meteorologiczna",
        ["Nie można połączyć się z Pogoda.by. Spróbuj ponownie.", "Katalog stacji jest pusty lub ma nieobsługiwany format.", "Stacja nie udostępnia teraz obsługiwanych danych pogodowych. Spróbuj ponownie lub wybierz inną stację.", "Wybierz kraj z listy.", "Wybierz stację z listy."],
        "Ta stacja została już dodana.", "Ustawienia aktualizacji", "Dane pogodowe są pobierane jednym zapytaniem RSS dla każdej stacji. Stacja może publikować nowe pomiary rzadziej.", "Interwał aktualizacji (minuty)",
        ["Temperatura", "Ciśnienie atmosferyczne", "Tendencja ciśnienia", "Prędkość wiatru", "Kierunek wiatru", "Pogoda", "Czas obserwacji", "Stacja meteorologiczna", "Wilgotność", "Porywy wiatru", "Widoczność"],
    ),
}

if __name__ == "__main__":
    (BASE / "translations").mkdir(exist_ok=True)
    for language, data in TRANSLATIONS.items():
        (BASE / "translations" / f"{language}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (BASE / "strings.json").write_text(json.dumps(TRANSLATIONS["en"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
