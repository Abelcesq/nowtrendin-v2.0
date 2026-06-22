---
name: project-todo-app-setup
description: Full stack todo app — React Native (Expo) frontend + Django REST backend deployed to Heroku with Postgres
metadata: 
  node_type: memory
  type: project
  originSessionId: 68bada2a-c5b3-4db5-a55b-bc9a4f6844d3
---

## Stack

- **Frontend:** React Native via Expo (blank template), lives in `frontend/`
- **Backend:** Django 6 + Django REST Framework, lives in `backend/`
- **Database (local):** SQLite (`backend/db.sqlite3`)
- **Database (production):** Heroku Postgres (auto-provisioned, connection via `DATABASE_URL`)

## Live URLs

- **Heroku API:** `https://nowtrendin-backend-acb79c396814.herokuapp.com/api/todos/`
- **GitHub repo:** `https://github.com/Abelcesq/nowtrendin-v2.0`

## Key files

- `frontend/App.js` — full todo UI (add, toggle complete, delete); `API_URL` points at Heroku
- `backend/config/settings.py` — Django settings; uses `dj-database-url` for DB, whitenoise for static files
- `backend/todos/models.py` — `Todo` model: `title`, `completed`, `created_at`
- `backend/Procfile` — `web: gunicorn config.wsgi --log-file -`
- `backend/requirements.txt` — pinned deps including gunicorn, whitenoise, psycopg2-binary

## How to run locally

**Backend:**
```bash
cd backend
venv/Scripts/python manage.py runserver
```

**Frontend (Expo Go on phone):**
```bash
cd frontend
npx expo start
# scan QR with Expo Go
```

> Phone uses the live Heroku URL, so no local IP swap needed.

## How to redeploy backend to Heroku

```bash
git add backend/
git commit -m "your message"
git subtree push --prefix backend heroku main
```

**Why:** Heroku remote is set at the repo root, but Heroku only needs the `backend/` subtree — `git subtree push` sends just that folder as the repo root to Heroku.
