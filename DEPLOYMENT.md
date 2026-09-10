# CineBook deployment

## 1. Deploy the backend to Render

Use the repository root as the Render Blueprint location. `render.yaml` creates a Python web service and a PostgreSQL database. The service starts with `gunicorn app:app` from the `backend` directory.

After the service is created, copy its public URL, for example `https://cinebook-api.onrender.com`.

Set the Render environment variable `FRONTEND_URL` to the final Vercel URL. `DATABASE_URL` and `SECRET_KEY` are created by the blueprint.

For a manual Render service, use:

- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Health check path: `/api/health`

A PostgreSQL database is recommended. SQLite is only a local fallback because Render's local filesystem is not permanent.

## 2. Deploy the frontend to Vercel

Create a Vercel project with `frontend` as the Root Directory and deploy it as a static site. Before deploying, replace `YOUR-RENDER-SERVICE.onrender.com` in `frontend/app.js` with the Render service hostname.

The Vercel rewrite in `frontend/vercel.json` keeps hash routes working on refresh. No build command is required.

## 3. Local development

Start the API from `backend` with `python app.py` and open `frontend/index.html`. The frontend automatically uses `http://localhost:5000` on localhost.

The original Flask-rendered pages remain available locally at `http://localhost:5000`.
