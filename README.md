# VetNexa AI

A Flask web application for AI-powered livestock disease detection across multiple animal types.

## Supported Animals
- **Dogs** — Skin disease detection (Dermatitis, Ringworm, Demodicosis, Fungal)
- **Cattle** — Disease detection (Foot & Mouth, Lumpy Skin Disease)
- **Goats** — Skin condition detection (Scabies, Ringworm, Flea Allergy)
- **Poultry** — Disease detection via fecal image analysis (Coccidiosis, Salmonella, Newcastle)

## Requirements
- Python 3.10
- See `requirements.txt` for all dependencies

## Setup

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

## Project Structure

- `app.py` — Main Flask application entry point
- `dogs/` — Dog disease model and routes
- `cattle/` — Cattle disease model and routes
- `goats/` — Goat disease model and routes
- `poultry/` — Poultry disease model and routes
- `templates/` — HTML templates for all pages
- `static/` — CSS, JavaScript, and image assets
- `disease_info.py` — Disease information database
- `database.py` — Database connection
- `auth_routes.py` — Authentication routes
