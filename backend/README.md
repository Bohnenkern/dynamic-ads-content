# Backend - FastAPI

## Setup

1. Erstelle eine virtuelle Umgebung:
```bash
python -m venv venv
```

2. Aktiviere die virtuelle Umgebung:
```bash
# Windows
.\venv\Scripts\activate
```

3. Installiere die Dependencies:
```bash
pip install -r requirements.txt
```

4. Kopiere `.env.example` nach `.env` und passe die Werte an:
```bash
cp .env.example .env
```

## Starten des Servers

```bash
python main.py
```

Oder mit uvicorn direkt:
```bash
uvicorn main:app --reload
```

Der Server läuft auf: http://localhost:8000

API-Dokumentation: http://localhost:8000/docs
