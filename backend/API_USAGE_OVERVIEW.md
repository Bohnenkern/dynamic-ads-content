# 📊 API Usage Overview - Dynamic Ads Content

## 🔒 Implementierte Limits (Schutz vor API-Übernutzung)

### Black Forest Labs API
- **MAX_IMAGES_PER_CAMPAIGN: 5**
- Pro Campaign werden maximal 5 Bilder generiert
- Schutz vor versehentlicher Übernutzung des API Keys

### OpenAI API
- **MAX_TRENDS_FOR_OPTIMIZATION: 5**
- Nur die Top 5 Trends werden mit GPT-4o optimiert
- Reduziert teure GPT-4o Aufrufe

## 📈 API Aufrufe pro Campaign Generation

### OpenAI API Aufrufe

#### GPT-4o-mini (günstiger)
1. **Trend Filtering** (Step 3): 1 Aufruf
   - Filtert 20 Trends auf campaign-geeignete Trends
   - Modell: `gpt-4o-mini`

2. **Interest Matching** (Step 4): 5 Aufrufe (1 pro User)
   - Matched User-Interessen mit Trends (semantisch)
   - Modell: `gpt-4o-mini`

**Gesamt GPT-4o-mini: 6 Aufrufe pro Campaign**

#### GPT-4o (teurer, für kreative Optimierung)
3. **Prompt Optimization** (Step 6): max. 5 Aufrufe
   - Optimiert Bild-Prompts für Black Forest API
   - Limitiert auf Top 5 Trends nach User-Matches
   - Modell: `gpt-4o`

**Gesamt GPT-4o: max. 5 Aufrufe pro Campaign**

**Total OpenAI: 11 API Aufrufe pro Campaign**

### Black Forest Labs API Aufrufe

4. **Image Generation** (Step 7): max. 5 Aufrufe
   - Generiert Bilder für die Top 5 Trends
   - HARD LIMIT: Maximal 5 Bilder pro Campaign
   - Modell: `FLUX.2-pro-1.1`

**Gesamt Black Forest: max. 5 Aufrufe pro Campaign**

## 🎯 Intelligente Trend-Auswahl

Die Top 5 Trends werden ausgewählt basierend auf:

1. **User Match Count**: Wie viele User haben diesen Trend gematcht?
2. **Popularity Score**: Wie populär ist der Trend generell?

Beispiel:
```
Sports & Fitness: 4 users matched → hohe Priorität
Technology & AI: 3 users matched → mittlere Priorität
Gaming: 5 users matched → höchste Priorität ✅
```

## 💰 Kostenabschätzung (ungefähr)

### Pro Campaign Generation:
- **GPT-4o-mini**: 6 Aufrufe × ~$0.0001 = **$0.0006**
- **GPT-4o**: 5 Aufrufe × ~$0.01 = **$0.05**
- **Black Forest**: 5 Bilder × ~$0.04 = **$0.20**

**Total pro Campaign: ~$0.25**

### Bei 10 Campaigns pro Tag:
- OpenAI: ~$0.50/Tag
- Black Forest: ~$2.00/Tag
- **Total: ~$2.50/Tag oder ~$75/Monat**

## 🚀 Workflow mit Limits

```
Campaign Start
    ↓
[Step 1] Image Upload ✅
    ↓
[Step 2] Load 20 Trends ✅
    ↓
[Step 3] OpenAI Filter → ~15 suitable trends (1 API call)
    ↓
[Step 4] Match with 5 Users (5 API calls - GPT-4o-mini)
    ↓
[Step 5] Build 5 Structured Prompts ✅
    ↓
[Step 6] Select TOP 5 Trends by matches + popularity
         Optimize with GPT-4o (5 API calls - GPT-4o)
    ↓
[Step 7] Generate MAX 5 Images (5 API calls - Black Forest) 🔒
    ↓
[Step 8] Map Images to Users ✅
    ↓
Campaign Complete
```

## 📊 Response Format

Die API gibt jetzt detaillierte Usage-Statistics zurück:

```json
{
  "campaign_theme": "Samsung S20 Launch",
  "selected_trends_count": 5,
  "selected_trends": [
    {
      "category": "Gaming",
      "interests": ["Video Gaming", "PC Gaming", ...],
      "user_matches": 5
    },
    ...
  ],
  "trend_images_generated": 5,
  "api_usage": {
    "openai_gpt4o_mini_calls": 6,
    "openai_gpt4o_calls": 5,
    "black_forest_calls": 5,
    "total_openai_calls": 11,
    "image_limit": 5,
    "optimization_limit": 5
  }
}
```

## ⚙️ Anpassung der Limits

Die Limits können in `backend/routers/users.py` angepasst werden:

```python
# API Call Limits to prevent overuse
MAX_IMAGES_PER_CAMPAIGN = 5  # Black Forest API limit
MAX_TRENDS_FOR_OPTIMIZATION = 5  # OpenAI GPT-4o limit
```

### Empfohlene Einstellungen:

**Entwicklung/Testing:**
- MAX_IMAGES_PER_CAMPAIGN = 2
- MAX_TRENDS_FOR_OPTIMIZATION = 2

**Production (Standard):**
- MAX_IMAGES_PER_CAMPAIGN = 5
- MAX_TRENDS_FOR_OPTIMIZATION = 5

**High-Budget Campaign:**
- MAX_IMAGES_PER_CAMPAIGN = 10
- MAX_TRENDS_FOR_OPTIMIZATION = 10

## 🔍 Logging

Alle API-Aufrufe werden geloggt:

```
📊 API USAGE STATISTICS:
   • OpenAI GPT-4o-mini calls: 6
   • OpenAI GPT-4o calls: 5
   • Black Forest image generations: 5/5
   • Total OpenAI API calls: 11
```

## ⚠️ Wichtige Hinweise

1. **Black Forest Limit ist HART**: Niemals mehr als 5 Bilder pro Campaign
2. **Trend Selection ist intelligent**: Top Trends basierend auf User-Matches
3. **Alle Aufrufe werden gezählt**: Vollständige Transparenz über API Usage
4. **Cost Control**: ~$0.25 pro Campaign bei 5 Bildern
5. **Skalierbar**: Limits können jederzeit angepasst werden

## 📝 Changelog

### Version 2.0 (30.11.2025)
- ✅ 5-Bilder-Limit für Black Forest API implementiert
- ✅ Top 5 Trend Selection nach User-Matches
- ✅ Vollständige API Call Tracking
- ✅ Cost Statistics in Response
- ✅ Logging für alle API-Aufrufe
