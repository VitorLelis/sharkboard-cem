# Sharkboard (CEM Reporter)

Reporter for the FPN [CEM](https://www.fpnatacao.pt/modalidades.php?modalidade=m) ranks.

This is a standalone project that reads the PostgreSQL database used by the main Phoenix project and generates `report.pdf`.

Original project:

[Sharkboard](https://github.com/VitorLelis/sharkboard)

## Install

```bash
pip3 install -r requirements.txt
```

## Configuration

Create a `.env` file:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=phoenix
DB_USER=postgres
DB_PASSWORD=your_password

SEASON=2025/2026
HIGHLIGHT_CLUB=SCB
```

## Run

```bash
python3 main.py
```

The report will be generated as:

```text
report.pdf
```
