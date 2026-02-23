# MCP Server Rehberi

Tek bir MCP sunucusu (`python -m server.mcp`) ile **widget yonetimi**, **hava durumu**, **tatil/ozel gunler**, **trendler**, **data source'lar** ve **Gemini AI orkestrasyonu** hepsi bir arada kullanilir.

---

## Mimari

```
Cursor / Claude Desktop (MCP Client)
        |
        | stdin/stdout (MCP protocol)
        |
   server/mcp/server.py (MCP Server)
        |
        +-- tool_definitions.py   ← 20 tool tanimi (single source of truth)
        |
        +-- handlers/
        |    ├── widget_handlers.py   (CRUD + trigger)
        |    ├── weather_handlers.py  (OpenWeatherMap)
        |    ├── holiday_handlers.py  (tatil/ozel gunler)
        |    ├── trend_handlers.py    (viral trendler)
        |    └── ai_handlers.py       (data sources + AI suggest)
        |
        +-- agent.py → Gemini AI (ask tool — tool orchestration)
```

### Handler Registry Pattern

Tool'lar `tool_definitions.py`'da tanimlanir, handler'lar domain modullere ayrilir. `server.py` bunlari bir registry dict ile birlestirir. Herhangi bir handler hata verse bile sunucu dusmez (global error wrapper).

### Single Source of Truth

`tool_definitions.py` hem MCP server (list_tools/call_tool) hem de Gemini agent (function declarations) tarafindan kullanilir. Boylece tool tanimlari asla senkrondan cikmaz.

---

## Araclar (20 Tool)

| Kategori | Tool'lar |
|----------|----------|
| **Widget** | `create_widget`, `list_widgets`, `update_widget`, `delete_widget`, `create_trigger_rule`, `evaluate_triggers`, `get_widget_catalog` |
| **Weather** | `get_current_weather`, `get_weather_forecast`, `get_weather_by_coords` |
| **Holidays** | `get_today_holidays`, `get_holidays_by_date`, `get_upcoming_holidays`, `get_holidays_for_month`, `suggest_widget_for_holiday` |
| **Trends** | `get_trends`, `suggest_from_trends` |
| **Data Sources** | `get_data_sources`, `suggest_widgets` |
| **Gemini Agent** | `ask` — dogal dilde soru/istek; Gemini gerekirse diger tool'lari cagirip cevabi birlestirir |

---

## Ask (Gemini Orkestrasyonu)

`ask` tool'una dogal dilde bir cumle yazarsiniz. Gemini, tanimli araclar arasinden secim yapip cagirip sonuclari birlestirir.

Ornekler:
- *"Istanbul'da hava nasil?"* → `get_current_weather("Istanbul")` → ozet
- *"Istanbul hava durumuna gore bana widget oner"* → hava bilgisi + `suggest_widgets`
- *"Bugun ozel gun var mi?"* → `get_today_holidays`
- *"Firebase'te kac widget var?"* → `list_widgets`
- *"Yarin icin hava durumuna dayali widget olustur"* → hava + `create_widget`

Agent MAX_TURNS=10 ile agentic loop calistirir — bir soru icin birden fazla tool cagirabilir.

---

## Kurulum

### 1. Cursor

1. Cursor → **Settings** → **MCP** → "Edit in settings.json"
   - Veya dogrudan `~/.cursor/mcp.json` (macOS/Linux) / `%USERPROFILE%\.cursor\mcp.json` (Windows)
   - Proje bazli: proje kokunde `.cursor/mcp.json`

2. `mcp_config.example.json` icerigini kopyalayip duzeleyin:

```json
{
  "mcpServers": {
    "intyx-dynamic-widget": {
      "command": "python",
      "args": ["-m", "server.mcp"],
      "cwd": "/PROJE/YOLUNUZ/intyx-dynamic-widget",
      "env": {
        "FIREBASE_PROJECT_ID": "intyx-dynamic",
        "GEMINI_API_KEY": "your-gemini-api-key",
        "FIREBASE_CREDENTIALS_PATH": "/path/to/serviceAccountKey.json",
        "OPENWEATHER_API_KEY": "optional-for-weather"
      }
    }
  }
}
```

3. Kaydedin ve Cursor'i yeniden baslatin (veya MCP sunucularini yeniden yukleyin).

### 2. Claude Desktop

Claude Desktop MCP ayarlarinda ayni config'i kullanin. `command` ve `args` ayni.

### 3. Diger MCP Client'lar

Herhangi bir MCP client stdio transport destekliyorsa:
```bash
cd /path/to/intyx-dynamic-widget
FIREBASE_PROJECT_ID=intyx-dynamic GEMINI_API_KEY=your-key python -m server.mcp
```

---

## Kullanim

### Cursor'da

1. **Composer veya Chat'i acin** (Cmd+I / Ctrl+I)
2. MCP tool'larini secin — **intyx-dynamic-widget** sunucusundaki araclardan birini secin
3. **Ask (dogal dil):** `ask` tool'unu secin, `query` alanina yazin
4. **Tekil araclar:** `get_current_weather` → `city: Istanbul`

### Terminalden Test

```bash
cd /path/to/intyx-dynamic-widget
export FIREBASE_PROJECT_ID=intyx-dynamic
export GEMINI_API_KEY=your-key
python -m server.mcp
```

Stdio uzerinden MCP protokolu dinler. `Ctrl+C` ile durdurun.

---

## Gereksinimler

| Gereksinim | Aciklama |
|-----------|----------|
| Python 3.10+ | MCP server Python'la calisir |
| `pip install -r server/requirements.txt` | mcp, google-generativeai, firebase-admin, vb. |
| `FIREBASE_PROJECT_ID` | Zorunlu env |
| `GEMINI_API_KEY` | Zorunlu env (ask tool icin) |
| `FIREBASE_CREDENTIALS_PATH` | Opsiyonel (yerel icin) |
| `OPENWEATHER_API_KEY` | Opsiyonel (weather tool'lari icin) |

---

## Sorun Giderme

| Sorun | Cozum |
|-------|-------|
| "GEMINI_API_KEY is required" | `.env` veya MCP config'deki `env` bolumune key'i ekleyin |
| Tool listesi gorunmuyor | Cursor'i yeniden baslatin, MCP sunucusunu reload edin |
| "Firebase connection error" | `FIREBASE_PROJECT_ID` dogru mu? Service account JSON yolu dogru mu? |
| Weather verisi gelmiyor | `OPENWEATHER_API_KEY` opsiyonel — eklenmezse placeholder veri doner |
