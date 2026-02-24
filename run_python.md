# Python Setup & Entwicklungsumgebung

Dieses Projekt verwendet **[uv](https://docs.astral.sh/uv/)** als Python Package Manager und **`.venv`** als lokale virtuelle Umgebung.

---

## Voraussetzungen

| Tool | Mindestversion | Installationscheck |
|------|---------------|-------------------|
| Python | 3.12 | `python3 --version` |
| uv | beliebig | `uv --version` |

### uv installieren (einmalig)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Danach Shell neu laden oder:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

---

## Ersteinrichtung (einmalig)

```bash
# 1. Python 3.12 pinnen
uv python pin 3.12

# 2. Virtuelle Umgebung erstellen
uv venv .venv
```

Das war es. uv lädt bei Bedarf automatisch die korrekte Python-Version herunter.

---

## Täglicher Workflow

### Virtuelle Umgebung aktivieren

```bash
source .venv/bin/activate
```

Deaktivieren:
```bash
deactivate
```

### Abhängigkeiten installieren

```bash
# Alle Abhängigkeiten aus pyproject.toml installieren
uv sync

# Neue Abhängigkeit hinzufügen
uv add <paketname>

# Entwicklungs-Abhängigkeit hinzufügen (z.B. pytest)
uv add --dev pytest
```

### Skript / Modul ausführen

```bash
# Ohne vorherige Aktivierung (uv managed)
uv run python src/quote_engine/...

# Mit aktivierter .venv
python src/quote_engine/...
```

---

## Projektstruktur (Python-relevant)

```
ai-project/
├── .python-version     # Pinned: 3.12 (von uv python pin)
├── pyproject.toml      # Projektdefinition & Abhängigkeiten
├── uv.lock             # Lockfile (committen!)
├── .venv/              # Lokale virtuelle Umgebung (nicht committen)
└── src/
    └── quote_engine/   # Hauptpaket
```

---

## IDE-Konfiguration

### IntelliJ IDEA / PyCharm

1. **File → Project Structure → SDKs → +**
2. Typ: **Python SDK** → **Existing environment**
3. Pfad: `.venv/bin/python` (absoluter Pfad)
4. **OK**

### VS Code

`.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"
}
```

Oder: `Ctrl+Shift+P` → **Python: Select Interpreter** → `.venv/bin/python` auswählen.

---

## Häufige Befehle (Kurzreferenz)

| Aktion | Befehl |
|--------|--------|
| Umgebung erstellen | `uv venv .venv` |
| Umgebung aktivieren | `source .venv/bin/activate` |
| Pakete installieren | `uv sync` |
| Paket hinzufügen | `uv add <name>` |
| Dev-Paket hinzufügen | `uv add --dev <name>` |
| Skript ausführen | `uv run python <datei>` |
| Tests ausführen | `uv run pytest` |
| Python-Version prüfen | `python --version` |

---

## .gitignore

Folgende Einträge gehören in `.gitignore`:

```
.venv/
__pycache__/
*.pyc
.env
```

`uv.lock` und `.python-version` **werden committet** — sie sichern reproduzierbare Builds im Team.
