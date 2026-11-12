# Pogoda.by v0.1.1

## Русский

Обновление интеграции Home Assistant для получения фактической погоды с Pogoda.by.

### Изменения

- Добавлена поддержка установки и обновления через Marketplace в Home Assistant 2026.11 и новее, а также через HACS на более ранних версиях. Используется пользовательский репозиторий `Toropyga/pogoda_by`.
- Интервал обновления по умолчанию увеличен до **1 часа**. В настройках можно выбрать от 5 до 180 минут. Ранее сохранённые пользовательские интервалы сохраняются.
- Добавлена иконка **Pogoda.by** с прозрачным фоном в размерах 256×256 и 512×512. Локальное отображение иконки поддерживается в Home Assistant 2026.3 и новее.
- Интерфейс доступен на **русском, английском, польском и белорусском** языках. Переведены формы настройки, сообщения об ошибках и названия сенсоров.
- README доступен на четырёх языках; обновлены инструкции установки и добавлены ссылки для переключения языков.

Интеграция позволяет выбрать страну и метеостанцию и получать температуру, давление, ветер, описание погоды, время наблюдения и сведения о станции. Дополнительные поля создаются только при их наличии в RSS.

### Установка и обновление

Откройте **Настройки → Marketplace → Add from link**, добавьте `https://github.com/Toropyga/pogoda_by` и установите интеграцию. На старых версиях Home Assistant добавьте этот адрес в пользовательские репозитории HACS с типом **Integration**. После обновления перезапустите Home Assistant по уведомлению системы.

Подробности и ручная установка: [README на русском](https://github.com/Toropyga/pogoda_by/blob/v0.1.1/README.md).

### Проверка и ограничения

Пройдены **36 автономных тестов**. Полная установка через Marketplace / HACS и запуск внутри Home Assistant ещё не проверены в среде разработки. Текстовые значения из RSS сохраняются на языке источника. Интеграция предоставляет наблюдения, а не прогноз погоды.

---

## English

An update to the Home Assistant integration for weather observations from Pogoda.by.

### Changes

- Added installation and update support for the built-in Marketplace in Home Assistant 2026.11 and later, and HACS on earlier versions. Add `Toropyga/pogoda_by` as a custom repository.
- Increased the default update interval to **1 hour**. The interval is configurable from 5 to 180 minutes. Previously saved custom intervals are retained.
- Added a **Pogoda.by** icon with a transparent background in 256×256 and 512×512 sizes. Local integration icons require Home Assistant 2026.3 or later.
- The interface is available in **English, Russian, Polish and Belarusian**, including setup forms, error messages and sensor names.
- The README is available in all four languages, with updated installation instructions and language navigation links.

Select a country and weather station to monitor temperature, pressure, wind, weather descriptions, observation time and station metadata. Additional fields are created only when provided by the RSS feed.

### Installation and updates

Open **Settings → Marketplace → Add from link**, add `https://github.com/Toropyga/pogoda_by` and install the integration. On earlier Home Assistant versions, add the same URL to HACS custom repositories with the **Integration** type. After updating, restart Home Assistant when prompted.

Details and manual installation: [English README](https://github.com/Toropyga/pogoda_by/blob/v0.1.1/README.en.md).

### Validation and limitations

All **36 offline tests pass**. Full installation through Marketplace / HACS and execution inside Home Assistant have not yet been verified in the development environment. RSS text values retain the provider's language. The integration supplies weather observations, not forecasts.
