
# CardNews MVP – Quick Start on AWS EC2 (✈️ Poetry edition)

> **TL;DR**  
> Clone → set `.env` → `poetry install` → `playwright install chromium` → run Uvicorn.

---

## 1. Clone the repo

```bash
git clone <YOUR‑REPO‑URL>
```

---

## 2. Create `.env`

The app expects these keys (example values):

```dotenv
PROXY_HOST=gate.decodo.com
PROXY_USER=yourProxyUser
PROXY_PASS=yourProxyPass

OPENAI_API_KEY=sk-xxxx
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
API_HASH_SECRET=your256bitHex
```

Put the file at the project root **before** starting the service.

---

## 3. Install dependencies (Poetry)

```bash
# Install Poetry once on the instance if missing
curl -sSL https://install.python-poetry.org | python3 -

# Use Python 3.11+
poetry env use 3.11          # optional – picks system python3.11

# Install locked dependencies (no editable install)
poetry install
```

This reads the included *pyproject.toml* / *poetry.lock* and creates an isolated virtual‑env under `.venv/`.

---

## 4. Install Playwright browser (first time only)

Camoufox needs a headless Chromium:

```bash
poetry run playwright install chromium
```

*(~70 MB download; runs once per machine)*

---

## 5. Run the API

```bash
poetry run uvicorn cardnews.main:app --host 0.0.0.0 --port 8000
```

Open `http://<EC2‑PUBLIC‑IP>:8000/docs` to try the interactive Swagger UI.

---

## 6. Test Get Request 

```bash
curl -G "http://localhost:8000/generate" \
  --data-urlencode "q=엄마선물추천" \
  --data-urlencode "range=None" \
  --header "X-Api-Key:<API_KEY>" \
  --header "Accept: application/json"
```

Open `http://<EC2‑PUBLIC‑IP>:8000/docs` to try the interactive Swagger UI.

---

### Production hints

* Put the above command in a **systemd** service or **PM2** / **supervisor** job for auto‑restart.  
* Use an **Nginx** reverse proxy for TLS & compression.  
* For zero‑downtime redeploys, restart a second instance, swap ALB target, then terminate the old one.

---

Happy shipping! 🚀
