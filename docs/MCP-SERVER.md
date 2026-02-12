# MCP Server — Tek sunucu, Weather + Firebase + Holidays + Gemini

Tek bir MCP sunucusu (`python -m server.mcp`) ile **weather**, **Firebase** (widgets, trigger rules, cache, trends), **holidays** ve **Gemini** hepsi bir arada kullanılır. Gemini, **ask** tool’u ile bu araçları orkestre eder.

---

## Araçlar (tools)

| Kategori | Tool'lar |
|----------|----------|
| **Firebase** | create_widget, list_widgets, update_widget, delete_widget, create_trigger_rule, evaluate_triggers, get_data_sources, get_widget_catalog, get_trends, suggest_widgets, suggest_from_trends |
| **Weather** | get_current_weather, get_weather_forecast, get_weather_by_coords |
| **Holidays** | get_today_holidays, get_holidays_by_date, get_upcoming_holidays, get_holidays_for_month, suggest_widget_for_holiday |
| **Gemini agent** | **ask** — Doğal dilde soru/istek; Gemini gerekirse weather, Firebase ve holidays araçlarını çağırıp cevabı verir. |

---

## Ask (Gemini orkestrasyonu)

**ask** tool’una doğal dilde bir cümle yazarsınız. Gemini, tanımlı araçlar (weather, list_widgets, get_today_holidays, get_data_sources, suggest_widgets, vb.) arasından seçim yapıp çağırır, sonuçları birleştirip metin cevap döner.

Örnekler:

- *"Istanbul'da hava nasil?"* → Gemini `get_current_weather("Istanbul")` çağırır, cevabı özetler.
- *"Istanbul hava durumuna gore bana bir widget oner"* → Önce hava bilgisi alır, sonra `suggest_widgets` ile context’e uygun widget önerir.
- *"Bugun ozel gun var mi?"* → `get_today_holidays` çağırır.
- *"Firebase’te kac widget var ve katalogda neler var?"* → `list_widgets` ve `get_widget_catalog` kullanır.

---

## Kurulum (Cursor)

1. **MCP config dosyası**
   - Cursor → **Settings** → **MCP** → “Edit in settings.json” veya doğrudan `~/.cursor/mcp.json` (macOS/Linux) / `%USERPROFILE%\.cursor\mcp.json` (Windows) açın.
   - Proje içinde kullanacaksanız: proje kökünde `.cursor/mcp.json` oluşturabilirsiniz.

2. **Config içeriği**
   - `mcp_config.example.json` dosyasını açıp içeriği kopyalayın.
   - `cwd`: projenin **tam yolu** (örn. `/Users/adiniz/Documents/Projects/intyx-dynamic-widget`).
   - `env` içinde:
     - `FIREBASE_PROJECT_ID`: Firebase proje ID (örn. `intyx-dynamic`).
     - `GEMINI_API_KEY`: Google AI Studio’dan aldığınız API key.
     - İsteğe bağlı: `FIREBASE_CREDENTIALS_PATH` (service account JSON yolu), `OPENWEATHER_API_KEY` (hava araçları için).

3. **Kaydedip Cursor’ı yenileyin**
   - Config’i kaydedin; gerekirse Cursor’ı yeniden başlatın veya MCP sunucularını yeniden yükleyin. Sunucu `python -m server.mcp` ile otomatik başlar.

---

## Kullanım (Cursor’da)

1. **Composer veya Chat’i açın** (Cmd+I / Ctrl+I veya sohbet paneli).
2. **MCP tool kullanmak için**
   - Composer’da genelde **@** veya **Tools** ile MCP araçları listelenir.
   - **intyx-dynamic-widget** sunucusundaki araçlardan birini seçin (örn. **ask**, get_current_weather, list_widgets).
3. **Ask (doğal dil)**
   - **ask** tool’unu seçin, **query** alanına doğal dilde yazın:
     - *Istanbul'da hava nasil?*
     - *Bugun ozel gun var mi?*
     - *Bana hava durumuna gore bir widget oner*
   - Gönder’e basın; Gemini gerekli araçları (weather, holidays, suggest_widgets vb.) kendisi çağırıp cevabı verir.
4. **Tekil araçlar**
   - Sadece hava istiyorsanız **get_current_weather** seçip `city: Istanbul` verin.
   - Widget listesi için **list_widgets**, katalog için **get_widget_catalog** kullanın.

---

## Terminalden test (isteğe bağlı)

Sunucunun ayağa kalktığını doğrulamak için proje kökünde:

```bash
cd /path/to/intyx-dynamic-widget
export FIREBASE_PROJECT_ID=intyx-dynamic
export GEMINI_API_KEY=your-key
python -m server.mcp
```

Stdio üzerinden MCP protokolü dinler; Cursor dışında bir MCP client bağlarsanız aynı komutla kullanılır.

---

Ayrı weather veya holidays MCP sunucuları (`server.mcp.weather`, `server.mcp.holidays`) artık zorunlu değil; hepsi ana sunucuda birleşti.
