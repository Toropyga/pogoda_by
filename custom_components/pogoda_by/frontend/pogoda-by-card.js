/* Pogoda.by Card 0.2.0 | MIT | Bundled with the Pogoda.by integration. */
(() => {
  "use strict";
  const VERSION = "0.2.0";
  const FIELDS = ["temperature", "pressure", "pressure_trend", "wind_speed", "wind_direction", "condition", "observation_time", "station", "humidity", "wind_gust", "visibility"];
  const DEFAULTS = { show_details: true, show_graph: true, show_observation: true, compact: false, hours_to_show: 24, stale_after: 180, language: "auto" };
  const TEXT = {
    en: { station: "Weather station", choose: "Choose a Pogoda.by station", name: "Custom title", temperature: "Temperature", pressure: "Pressure", wind_speed: "Wind", wind_direction: "Direction", humidity: "Humidity", wind_gust: "Gusts", visibility: "Visibility", observed: "Observed", current: "Recent observation", stale: "Old observation", unknownTime: "Observation time unknown", noData: "No data", unavailable: "Weather data unavailable", history: "Temperature history", historyError: "History could not be loaded. Check Recorder and refresh the page.", details: "Show additional readings", graph: "Show temperature history", observation: "Show observation time", compact: "Compact view", hours: "History (hours)", staleAfter: "Mark as old after (minutes)", language: "Language", auto: "Home Assistant language", loading: "Loading stations…", registryError: "Cannot read the entity registry. Reload the page or set entities in YAML.", noStations: "No Pogoda.by stations found. Add the integration first.", source: "Open station on Pogoda.by", time: "Time", demo: "Demonstration data" },
    ru: { station: "Метеостанция", choose: "Выберите станцию Pogoda.by", name: "Название карточки", temperature: "Температура", pressure: "Давление", wind_speed: "Ветер", wind_direction: "Направление", humidity: "Влажность", wind_gust: "Порывы", visibility: "Видимость", observed: "Наблюдение", current: "Свежие данные", stale: "Устаревшие данные", unknownTime: "Время наблюдения неизвестно", noData: "Нет данных", unavailable: "Погодные данные недоступны", history: "История температуры", historyError: "Не удалось загрузить историю. Проверьте Recorder и обновите страницу.", details: "Дополнительные показатели", graph: "График температуры", observation: "Время наблюдения", compact: "Компактный вид", hours: "История (часы)", staleAfter: "Считать устаревшими через (минуты)", language: "Язык", auto: "Язык Home Assistant", loading: "Загрузка станций…", registryError: "Не удалось прочитать реестр сущностей. Обновите страницу или задайте entities в YAML.", noStations: "Станции Pogoda.by не найдены. Сначала добавьте интеграцию.", source: "Открыть станцию на Pogoda.by", time: "Время", demo: "Демонстрационные данные" },
    pl: { station: "Stacja pogodowa", choose: "Wybierz stację Pogoda.by", name: "Tytuł karty", temperature: "Temperatura", pressure: "Ciśnienie", wind_speed: "Wiatr", wind_direction: "Kierunek", humidity: "Wilgotność", wind_gust: "Porywy", visibility: "Widoczność", observed: "Obserwacja", current: "Aktualne dane", stale: "Nieaktualne dane", unknownTime: "Nieznany czas obserwacji", noData: "Brak danych", unavailable: "Dane pogodowe niedostępne", history: "Historia temperatury", historyError: "Nie można wczytać historii. Sprawdź Recorder i odśwież stronę.", details: "Dodatkowe pomiary", graph: "Wykres temperatury", observation: "Czas obserwacji", compact: "Widok kompaktowy", hours: "Historia (godziny)", staleAfter: "Oznacz jako stare po (minuty)", language: "Język", auto: "Język Home Assistant", loading: "Wczytywanie stacji…", registryError: "Nie można odczytać rejestru encji. Odśwież stronę lub ustaw entities w YAML.", noStations: "Nie znaleziono stacji Pogoda.by. Najpierw dodaj integrację.", source: "Otwórz stację w Pogoda.by", time: "Czas", demo: "Dane demonstracyjne" },
    be: { station: "Метэастанцыя", choose: "Выберыце станцыю Pogoda.by", name: "Назва карткі", temperature: "Тэмпература", pressure: "Ціск", wind_speed: "Вецер", wind_direction: "Напрамак", humidity: "Вільготнасць", wind_gust: "Парывы", visibility: "Бачнасць", observed: "Назіранне", current: "Свежыя даныя", stale: "Састарэлыя даныя", unknownTime: "Час назірання невядомы", noData: "Няма даных", unavailable: "Даныя пра надвор'е недаступныя", history: "Гісторыя тэмпературы", historyError: "Не атрымалася загрузіць гісторыю. Праверце Recorder і абнавіце старонку.", details: "Дадатковыя паказчыкі", graph: "Графік тэмпературы", observation: "Час назірання", compact: "Кампактны выгляд", hours: "Гісторыя (гадзіны)", staleAfter: "Лічыць састарэлымі праз (хвіліны)", language: "Мова", auto: "Мова Home Assistant", loading: "Загрузка станцый…", registryError: "Не атрымалася прачытаць рэестр сутнасцяў. Абнавіце старонку або задайце entities у YAML.", noStations: "Станцыі Pogoda.by не знойдзены. Спачатку дадайце інтэграцыю.", source: "Адкрыць станцыю на Pogoda.by", time: "Час", demo: "Дэманстрацыйныя даныя" },
    de: { station: "Wetterstation", choose: "Pogoda.by-Station auswählen", name: "Kartentitel", temperature: "Temperatur", pressure: "Luftdruck", wind_speed: "Wind", wind_direction: "Richtung", humidity: "Luftfeuchtigkeit", wind_gust: "Böen", visibility: "Sichtweite", observed: "Beobachtung", current: "Aktuelle Beobachtung", stale: "Veraltete Beobachtung", unknownTime: "Beobachtungszeit unbekannt", noData: "Keine Daten", unavailable: "Wetterdaten nicht verfügbar", history: "Temperaturverlauf", historyError: "Verlauf konnte nicht geladen werden. Recorder prüfen und Seite neu laden.", details: "Zusätzliche Messwerte", graph: "Temperaturverlauf anzeigen", observation: "Beobachtungszeit anzeigen", compact: "Kompakte Ansicht", hours: "Verlauf (Stunden)", staleAfter: "Als veraltet markieren nach (Minuten)", language: "Sprache", auto: "Sprache von Home Assistant", loading: "Stationen werden geladen…", registryError: "Entitätsregister konnte nicht gelesen werden. Seite neu laden oder entities in YAML festlegen.", noStations: "Keine Pogoda.by-Stationen gefunden. Zuerst die Integration hinzufügen.", source: "Station auf Pogoda.by öffnen", time: "Zeit", demo: "Demonstrationsdaten" }
  };
  const registryCache = new WeakMap();
  const escape = value => String(value ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  const available = state => Boolean(state && !["unknown", "unavailable", ""].includes(state.state));
  const lang = (config, hass) => {
    const value = config?.language && config.language !== "auto" ? config.language : hass?.locale?.language || hass?.language || "en";
    return TEXT[value.split(/[-_]/)[0]] ? value.split(/[-_]/)[0] : "en";
  };
  const numeric = state => available(state) && Number.isFinite(Number(state.state));

  function normalize(config) {
    const result = { ...DEFAULTS, ...config };
    if (result.station && !/^[A-Z]{2}_[\w-]+$/.test(result.station)) throw new Error("station must be COUNTRY_STATION_ID, e.g. BY_26850");
    if (!Number.isInteger(result.hours_to_show) || result.hours_to_show < 1 || result.hours_to_show > 168) throw new Error("hours_to_show: 1–168");
    if (!Number.isInteger(result.stale_after) || result.stale_after < 5 || result.stale_after > 10080) throw new Error("stale_after: 5–10080 minutes");
    if (result.language !== "auto" && !TEXT[result.language]) throw new Error("language: auto, en, ru, pl, be, de");
    for (const key of ["show_details", "show_graph", "show_observation", "compact"]) {
      if (typeof result[key] !== "boolean") throw new Error(`${key} must be a boolean`);
    }
    if (result.name !== undefined && typeof result.name !== "string") throw new Error("name must be text");
    if (result.entities !== undefined) {
      if (!result.entities || typeof result.entities !== "object" || Array.isArray(result.entities)) throw new Error("entities must be a mapping");
      for (const [key, value] of Object.entries(result.entities)) {
        if (!FIELDS.includes(key) || typeof value !== "string" || !/^sensor\.[\w]+$/.test(value)) throw new Error(`Invalid entities.${key}`);
      }
    }
    return result;
  }

  // One shared read per connection per minute, including concurrent card previews.
  function registry(hass) {
    const connection = hass.connection || hass;
    let cached = registryCache.get(connection);
    if (!cached || Date.now() - cached.time > 60000) {
      cached = { time: Date.now(), promise: hass.callWS({ type: "config/entity_registry/list" }) };
      registryCache.set(connection, cached);
    }
    return cached.promise;
  }

  function stations(hass, entries = []) {
    const result = new Map();
    for (const entry of entries) {
      if (entry.platform !== "pogoda_by" || entry.disabled_by) continue;
      const field = FIELDS.find(key => entry.unique_id?.endsWith(`_${key}`));
      if (!field) continue;
      const id = entry.unique_id.slice(0, -field.length - 1);
      if (!/^[A-Z]{2}_[\w-]+$/.test(id)) continue;
      if (!result.has(id)) result.set(id, { id, name: id.replace("_", " · "), entities: {} });
      const station = result.get(id);
      station.entities[field] = entry.entity_id;
      if (field === "station" && available(hass.states[entry.entity_id])) station.name = hass.states[entry.entity_id].state;
    }
    // Station metadata also lets the editor list stations before the registry arrives.
    for (const [entityId, state] of Object.entries(hass.states || {})) {
      const a = state.attributes || {};
      if (!entityId.startsWith("sensor.") || !a.observation_url || !a.country || !a.station_id) continue;
      if (!String(a.observation_url).startsWith("https://pogoda.by/")) continue;
      const id = `${a.country}_${a.station_id}`;
      if (!/^[A-Z]{2}_[\w-]+$/.test(id)) continue;
      if (!result.has(id)) result.set(id, { id, name: a.name || id, entities: {} });
      const station = result.get(id);
      station.entities.station = entityId;
      if (available(state)) station.name = state.state;
    }
    return [...result.values()].sort((a, b) => a.name.localeCompare(b.name));
  }

  function weatherIcon(description) {
    const text = (description || "").toLowerCase();
    const snow = /снег|снеж|snow|śnie|schnee/.test(text);
    const rain = /дожд|дождж|rain|deszcz|regen|морос|мряк/.test(text);
    const storm = /гроз|навальн|thunder|burz|gewitter/.test(text);
    const fog = /туман|fog|mgł|nebel/.test(text);
    const clear = /ясно|яснае|clear|sunny|słonecz|wolkenlos|sonnig/.test(text) && !/неясно/.test(text);
    const partial = /малообл|небольшая облач|переменн|перамен|partly|części|heiter/.test(text);
    const cloud = '<path d="M27 65h43a16 16 0 0 0 0-32 23 23 0 0 0-43-4 18 18 0 0 0 0 36Z" fill="var(--pby-cloud,#c6daea)" stroke="var(--pby-cloud-line,#94b6cf)" stroke-width="2"/>';
    const sun = '<g stroke="#edb344" stroke-width="3.5" stroke-linecap="round"><path d="M35 8v6m0 38v6M10 33h6m38 0h6M17 15l4 4m28 28 4 4M17 51l4-4m28-28 4-4"/></g><circle cx="35" cy="33" r="14" fill="#f5c55b"/>';
    let content = clear ? sun : partial ? sun + cloud : cloud;
    if (!description) content = '<text x="48" y="61" text-anchor="middle" font-size="44" fill="currentColor">?</text>';
    if (fog) content = cloud + '<path d="M18 74h62M25 83h48" stroke="#94b6cf" stroke-width="4" stroke-linecap="round"/>';
    if (rain) content += '<path d="m30 73-4 9m24-9-4 9m24-9-4 9" stroke="#559fe0" stroke-width="4" stroke-linecap="round"/>';
    if (snow) content += '<g fill="#72b8e4"><circle cx="30" cy="78" r="3"/><circle cx="49" cy="85" r="3"/><circle cx="68" cy="78" r="3"/></g>';
    if (storm) content += '<path d="m49 58-12 18h12l-6 17 21-25H51l8-10Z" fill="#edb344"/>';
    return `<svg class="weather-icon" viewBox="0 0 96 96" aria-hidden="true">${content}</svg>`;
  }

  class RegistryElement extends HTMLElement {
    constructor() { super(); this.attachShadow({ mode: "open" }); this._entries = []; this._registryRead = 0; }
    set hass(value) { this._hass = value; this._readRegistry(); this._render(); }
    get hass() { return this._hass; }
    _readRegistry() {
      if (!this._hass?.callWS || Date.now() - this._registryRead < 60000) return;
      this._registryRead = Date.now();
      this._loading = true;
      registry(this._hass).then(entries => {
        this._entries = entries;
        this._registryError = false;
      }).catch(() => { this._registryError = true; }).finally(() => { this._loading = false; this._render(); });
    }
    _text() { return TEXT[lang(this._config, this._hass)]; }
  }

  const STYLE = `
    :host{display:block;height:100%;container-type:inline-size;--pby-accent:var(--primary-color,#3583b8)}
    *{box-sizing:border-box}ha-card{height:100%;overflow:hidden;color:var(--primary-text-color,#26384a);background:var(--ha-card-background,var(--card-background-color,#fff));border-radius:var(--ha-card-border-radius,16px)}
    .body{padding:22px 24px 18px}.top{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}.brand{font-size:10px;font-weight:750;letter-spacing:.16em;color:var(--secondary-text-color,#6c8193);margin-bottom:5px}.brand b{color:var(--pby-accent)}
    h2{font-size:23px;font-weight:600;line-height:1.25;margin:0;overflow-wrap:anywhere}.status{font-size:10px;line-height:1.4;padding:5px 8px;border-radius:20px;background:var(--secondary-background-color,#f1f5f8);color:var(--secondary-text-color,#6c8193);display:flex;align-items:center;gap:5px;max-width:48%}.dot{width:6px;height:6px;border-radius:50%;background:var(--success-color,#409d7d);flex:none}.status.old .dot{background:var(--warning-color,#d8942d)}.status.off .dot{background:var(--error-color,#cf5757)}
    .hero{display:flex;align-items:center;gap:14px;margin:17px 0 20px}.weather-icon{width:88px;height:88px;flex:none}.reading{flex:1;min-width:0}.temp{display:flex;align-items:flex-start;gap:6px;line-height:1.06;white-space:nowrap}.value{font-size:60px;font-weight:350;letter-spacing:-.055em}.unit{font-size:23px;padding-top:7px;color:var(--secondary-text-color,#6c8193)}.condition{font-size:14px;line-height:1.5;color:var(--secondary-text-color,#6c8193);margin-top:7px;overflow-wrap:anywhere}
    button{font:inherit;color:inherit;border:0;background:none;cursor:pointer;text-align:inherit;padding:0}button:focus-visible,a:focus-visible{outline:2px solid var(--pby-accent);outline-offset:4px;border-radius:4px}button:disabled{cursor:default}
    .metrics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px 20px;border-top:1px solid var(--divider-color,#e9eff3);padding-top:17px}.metric{min-width:0;display:grid;grid-template-columns:22px minmax(0,1fr);gap:8px;align-items:center}.metric ha-icon{--mdc-icon-size:20px;color:var(--pby-accent)}.label{font-size:11px;color:var(--secondary-text-color,#6c8193);line-height:1.45}.metric-value{font-size:15px;line-height:1.5;font-weight:550;overflow-wrap:anywhere}.sub{font-size:11px;line-height:1.5;color:var(--secondary-text-color,#6c8193);overflow-wrap:anywhere}
    .footer{border-top:1px solid var(--divider-color,#e9eff3);margin-top:17px;padding-top:12px;display:flex;align-items:flex-end;justify-content:space-between;gap:12px}.observed{font-size:11px;color:var(--secondary-text-color,#6c8193);line-height:1.6}.observed time{display:block;color:var(--primary-text-color,#26384a)}a{font-size:10px;letter-spacing:.02em;text-decoration:none;color:var(--pby-accent);flex:none}.message{font-size:14px;line-height:1.6;padding:12px 0;color:var(--secondary-text-color,#6c8193)}.notice{font-size:12px;color:var(--error-color,#cf5757);margin:0 0 15px}
    .history:not(:empty){border-top:1px solid var(--divider-color,#e9eff3);padding:5px 8px 4px}.history .message{padding:12px 16px}.compact .body{padding:16px 18px}.compact .hero{margin:10px 0 14px}.compact .weather-icon{width:64px;height:64px}.compact .value{font-size:45px}.compact h2{font-size:20px}.compact .metrics{gap:10px 16px;padding-top:12px}.compact .footer{margin-top:12px;padding-top:9px}
    @media(max-width:360px){.body{padding:18px}.value{font-size:49px}.weather-icon{width:74px;height:74px}.status{max-width:44%;font-size:9px}.metrics{gap:14px 12px}}
    @container(max-width:300px){.body,.compact .body{padding:14px}.top{flex-wrap:wrap}.status{max-width:100%}.hero{gap:8px}.weather-icon,.compact .weather-icon{width:56px;height:56px}.value,.compact .value{font-size:40px}.unit{font-size:18px}.metric{grid-template-columns:18px minmax(0,1fr);gap:5px}.metric-value{font-size:13px}.metrics{gap:12px 8px}}
    @media(prefers-reduced-motion:no-preference){.weather-icon{animation:pby-in .3s ease-out}@keyframes pby-in{from{opacity:.4}to{opacity:1}}}
  `;

  class PogodaByCard extends RegistryElement {
    constructor() {
      super(); this._graphGeneration = 0;
      this.shadowRoot.innerHTML = `<style>${STYLE}</style><ha-card><div class="summary"></div><div class="history"></div></ha-card>`;
      this.shadowRoot.addEventListener("click", event => {
        const entityId = event.target.closest("[data-entity]")?.dataset.entity;
        if (entityId) this.dispatchEvent(new CustomEvent("hass-more-info", { detail: { entityId }, bubbles: true, composed: true }));
      });
    }
    static getConfigElement() { return document.createElement("pogoda-by-card-editor"); }
    static getStubConfig(hass) { return { station: stations(hass)[0]?.id || "", show_graph: true }; }
    getCardSize() { return this._config?.show_graph ? 11 : this._config?.compact ? 5 : 7; }
    getGridOptions() { return { columns: 12, rows: "auto", min_columns: 6 }; }
    setConfig(config) { this._config = normalize(config); this._signature = ""; this._render(); }
    connectedCallback() {
      this._readRegistry(); this._render();
      this._timer = setInterval(() => { this._readRegistry(); this._render(); }, 60000);
    }
    disconnectedCallback() { clearInterval(this._timer); }
    _resolve() {
      const found = stations(this._hass, this._entries).find(s => s.id === this._config.station);
      return { id: this._config.station, name: found?.name || this._config.station || "Pogoda.by", entities: { ...found?.entities, ...this._config.entities } };
    }
    _format(state) {
      if (!available(state)) return "—";
      if (this._hass.formatEntityState) return this._hass.formatEntityState(state);
      return `${state.state}${state.attributes?.unit_of_measurement ? ` ${state.attributes.unit_of_measurement}` : ""}`;
    }
    _render() {
      if (!this._hass || !this._config) return;
      const t = this._text(), s = this._resolve(), states = this._hass.states;
      const get = key => states[s.entities[key]];
      const relevant = FIELDS.map(key => get(key));
      const signature = JSON.stringify([this._config, relevant, s.name, lang(this._config, this._hass), this._loading, this._registryError, Math.floor(Date.now() / 60000)]);
      if (signature !== this._signature) {
        this._signature = signature;
        const temp = get("temperature"), condition = get("condition"), wind = get("wind_speed"), pressure = get("pressure");
        const hasWeather = [temp, condition, wind, pressure].some(available);
        const time = available(get("observation_time")) ? Date.parse(get("observation_time").state) : NaN;
        const age = Date.now() - time;
        const validTime = Number.isFinite(time) && age >= -300000;
        const old = validTime && age > this._config.stale_after * 60000;
        const status = !hasWeather ? t.unavailable : !validTime ? t.unknownTime : old ? t.stale : t.current;
        const stateClass = !hasWeather ? "off" : old || !validTime ? "old" : "";
        const unit = temp?.attributes?.unit_of_measurement || "";
        const formatted = numeric(temp) ? this._format(temp) : "—";
        const tempValue = unit && formatted.endsWith(unit) ? formatted.slice(0, -unit.length).trim() : formatted;
        const metric = (key, icon, sub) => `<button class="metric" data-entity="${escape(s.entities[key])}" ${s.entities[key] ? "" : "disabled"}><ha-icon icon="mdi:${icon}" aria-hidden="true"></ha-icon><span><span class="label">${escape(t[key])}</span><br><span class="metric-value">${escape(this._format(get(key)))}</span>${sub ? `<span class="sub"><br>${escape(sub)}</span>` : ""}</span></button>`;
        const direction = available(wind) ? (available(get("wind_direction")) ? get("wind_direction").state : wind.attributes?.direction) : undefined;
        const trend = available(pressure) ? (available(get("pressure_trend")) ? get("pressure_trend").state : pressure.attributes?.status) : undefined;
        const metrics = this._config.show_details ? `<div class="metrics">${metric("wind_speed", "weather-windy", direction)}${metric("pressure", "gauge", trend)}${[["humidity", "water-percent"], ["wind_gust", "windsock"], ["visibility", "eye-outline"]].filter(([key]) => available(get(key))).map(([key, icon]) => metric(key, icon)).join("")}</div>` : "";
        let date = t.unknownTime;
        if (validTime) {
          try { date = new Intl.DateTimeFormat(lang(this._config, this._hass), { dateStyle: "medium", timeStyle: "short", timeZone: this._hass.config?.time_zone }).format(time); }
          catch { date = new Date(time).toLocaleString(); }
        }
        const stationId = s.id?.match(/^[A-Z]{2}_(\d+)$/)?.[1];
        const source = stationId ? `<a href="https://pogoda.by/observation/meteo-observation/${stationId}" target="_blank" rel="noopener noreferrer" aria-label="${escape(t.source)}">Pogoda.by ↗</a>` : "";
        let body;
        if (!s.id && !Object.keys(this._config.entities || {}).length) body = `<div class="message">${escape(t.choose)}</div>`;
        else if (!Object.keys(s.entities).length) body = `<div class="message">${escape(this._loading ? t.loading : this._registryError ? t.registryError : t.noStations)}</div>`;
        else body = `<div class="top"><div><div class="brand"><b>POGODA</b>.BY</div><h2>${escape(this._config.name || s.name)}</h2></div><div class="status ${stateClass}" role="status"><i class="dot"></i>${escape(status)}</div></div><div class="hero">${weatherIcon(available(condition) ? condition.state : "")}<div class="reading"><button class="temp" ${s.entities.temperature ? `data-entity="${escape(s.entities.temperature)}"` : "disabled"} aria-label="${escape(t.temperature)}"><span class="value">${escape(tempValue)}</span><span class="unit">${escape(numeric(temp) ? unit : "")}</span></button><div class="condition">${escape(available(condition) ? condition.state : t.noData)}</div></div></div>${!hasWeather ? `<p class="notice">${escape(t.unavailable)}</p>` : ""}${metrics}${this._config.show_observation || source ? `<div class="footer">${this._config.show_observation ? `<div class="observed">${escape(t.observed)}${validTime ? `<time datetime="${new Date(time).toISOString()}">${escape(date)}</time>` : `<span><br>${escape(date)}</span>`}</div>` : "<span></span>"}${source}</div>` : ""}`;
        this.shadowRoot.querySelector(".summary").innerHTML = `<div class="${this._config.compact ? "compact" : ""}"><div class="body">${body}</div></div>`;
      }
      this._renderHistory(s);
    }
    _renderHistory(station) {
      const entity = station.entities.temperature;
      const key = this._config.show_graph && entity ? `${entity}|${this._config.hours_to_show}|${lang(this._config, this._hass)}` : "";
      const container = this.shadowRoot.querySelector(".history");
      if (key === this._graphKey) { if (this._graph) this._graph.hass = this._hass; return; }
      this._graphKey = key;
      const generation = ++this._graphGeneration;
      this._graph = undefined; container.replaceChildren();
      if (!key) return;
      Promise.resolve().then(() => {
        if (!window.loadCardHelpers) throw new Error("Card helpers unavailable");
        return window.loadCardHelpers();
      }).then(helpers => {
        if (generation !== this._graphGeneration) return;
        const graph = helpers.createCardElement({ type: "history-graph", title: this._text().history, hours_to_show: this._config.hours_to_show, entities: [{ entity, name: this._text().temperature }] });
        graph.style.cssText = "--ha-card-box-shadow:none;--ha-card-border-width:0;--ha-card-background:transparent;--ha-card-border-radius:0;";
        graph.hass = this._hass;
        this._graph = graph; container.replaceChildren(graph);
      }).catch(() => {
        if (generation === this._graphGeneration) container.innerHTML = `<p class="message">${escape(this._text().historyError)}</p>`;
      });
    }
  }

  class PogodaByCardEditor extends RegistryElement {
    setConfig(config) { this._config = normalize(config); this._render(); }
    connectedCallback() { this._readRegistry(); this._render(); }
    _render() {
      if (!this._hass || !this._config) return;
      const t = this._text(), list = stations(this._hass, this._entries);
      const signature = JSON.stringify([this._config, list, t, this._loading, this._registryError]);
      if (signature === this._signature) return;
      this._signature = signature;
      const selected = this._config.station;
      if (selected && !list.some(s => s.id === selected)) list.push({ id: selected, name: selected });
      const toggle = (key, label) => `<label class="toggle"><span>${escape(label)}</span><input type="checkbox" data-key="${key}" ${this._config[key] ? "checked" : ""}></label>`;
      this.shadowRoot.innerHTML = `<style>:host{display:block;color:var(--primary-text-color,#26384a)}*{box-sizing:border-box}.form{display:grid;gap:16px;padding:8px 0}label{font:inherit;display:grid;gap:6px;font-size:14px}input,select{font:inherit;color:inherit;background:var(--card-background-color,#fff);border:1px solid var(--divider-color,#aab7c2);border-radius:8px;padding:11px;width:100%;min-width:0}.toggle{display:flex;align-items:center;justify-content:space-between;gap:20px}.toggle input{width:20px;height:20px;accent-color:var(--primary-color,#3583b8)}.row{display:grid;grid-template-columns:1fr 1fr;gap:12px}p{font-size:13px;line-height:1.5;color:var(--secondary-text-color,#6c8193);margin:0}input:focus-visible,select:focus-visible{outline:2px solid var(--primary-color,#3583b8);outline-offset:2px}</style><div class="form"><label>${escape(t.station)}<select data-key="station"><option value="">${escape(t.choose)}</option>${list.map(s => `<option value="${escape(s.id)}" ${s.id === selected ? "selected" : ""}>${escape(s.name)} · ${escape(s.id)}</option>`).join("")}</select></label>${this._loading || this._registryError || !list.length ? `<p>${escape(this._loading ? t.loading : this._registryError ? t.registryError : t.noStations)}</p>` : ""}<label>${escape(t.name)}<input data-key="name" value="${escape(this._config.name || "")}"></label>${toggle("show_details", t.details)}${toggle("show_graph", t.graph)}${toggle("show_observation", t.observation)}${toggle("compact", t.compact)}<div class="row"><label>${escape(t.hours)}<input data-key="hours_to_show" type="number" min="1" max="168" step="1" value="${this._config.hours_to_show}"></label><label>${escape(t.staleAfter)}<input data-key="stale_after" type="number" min="5" max="10080" step="1" value="${this._config.stale_after}"></label></div><label>${escape(t.language)}<select data-key="language">${Object.entries({ auto: t.auto, ru: "Русский", be: "Беларуская", pl: "Polski", en: "English", de: "Deutsch" }).map(([key, name]) => `<option value="${key}" ${this._config.language === key ? "selected" : ""}>${escape(name)}</option>`).join("")}</select></label></div>`;
      this.shadowRoot.querySelector(".form").addEventListener("change", event => {
        const input = event.target, key = input.dataset.key;
        if (!key || !input.reportValidity()) return;
        const value = input.type === "checkbox" ? input.checked : input.type === "number" ? Number(input.value) : input.value;
        const next = { ...this._config, [key]: value };
        // Keep standard Lovelace options (visibility, grid_options, etc.).
        this._config = normalize(next);
        this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: { ...this._config } }, bubbles: true, composed: true }));
        this._render();
      });
    }
  }

  if (!customElements.get("pogoda-by-card")) customElements.define("pogoda-by-card", PogodaByCard);
  if (!customElements.get("pogoda-by-card-editor")) customElements.define("pogoda-by-card-editor", PogodaByCardEditor);
  window.customCards = window.customCards || [];
  if (!window.customCards.some(card => card.type === "pogoda-by-card")) window.customCards.push({ type: "pogoda-by-card", name: "Pogoda.by Card", description: "Observed weather from Pogoda.by · Фактическая погода", preview: true });
  console.info(`Pogoda.by Card ${VERSION}`);
})();
