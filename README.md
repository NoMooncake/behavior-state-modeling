# behavior-state-modeling

## Setup

Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows PowerShell
```

Install dependencies:

```bash
pip install -r requirements.txt
# optional for notebooks/EDA:
pip install -r requirements-dev.txt
```

## Generate sample data

```bash
python -m src.generate_data
```

**Outputs:**

- `data/sample/v0_1/events_sample.csv`
- `data/sample/v0_1/sessions_sample.csv`
- `data/sample/v0_1/generation_meta.csv`