# Deploying AgroAI on Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/adarshkumar247/AgroAI)

One Render web service runs the FastAPI backend and serves the static frontend
from the same URL:

```text
https://agroai-api-xxxx.onrender.com/
├── /                    → index.html (AgroAI UI)
├── /js/*                → frontend modules
├── /assets/*            → logos, avatars and sample images
├── /api/v1/*            → FastAPI endpoints
├── /uploads/*           → uploaded scans and profile photos
└── /docs                → Swagger API documentation
```

The frontend automatically calls the API on the same origin, so there is no
hard-coded backend URL to change.

---

## Step 1 — Push the deployment files

The repository already contains:

- `Dockerfile` — installs CPU PyTorch and starts Uvicorn
- `.dockerignore` — excludes `.env`, `.venv`, databases and uploads from the image
- `render.yaml` — Render Blueprint configuration
- `backend/app/main.py` — serves `index.html`, `js/` and `assets/`

Commit and push any local changes first:

```powershell
git add .
git commit -m "Add single-service Render deployment"
git push
```

---

## Step 2 — Create the Render service

1. Sign in at <https://render.com> with GitHub.
2. Click **New +** → **Blueprint**.
3. Select `adarshkumar247/AgroAI` and click **Connect**.
4. Render reads `render.yaml` automatically:
   - Name: `agroai-api`
   - Runtime: Docker
   - Plan: Free
   - Branch: `main`
   - Health check: `/api/v1/health`
5. When prompted for `GEMINI_API_KEY`, paste your Google Gemini key. This is
   optional — without it the AI assistant returns built-in fallback guidance.
6. Click **Apply** / **Create**.

The first Docker build takes roughly **5–10 minutes** because PyTorch is
installed. Later deploys are faster.

### Alternative: manual web service

If you do not want to use the Blueprint:

1. **New +** → **Web Service** → connect the repo.
2. Language: **Docker**.
3. Dockerfile path: `./Dockerfile`.
4. Plan: **Free**.
5. Health check path: `/api/v1/health`.
6. Add `GEMINI_API_KEY` (optional) and `GEMINI_MODEL=gemini-3.5-flash-lite`.

---

## Step 3 — Open the app

After the deploy finishes, Render gives you a URL such as:

```text
https://agroai-api-xxxx.onrender.com
```

Open it in a browser. The AgroAI login page should load.

Verify the backend too:

- <https://agroai-api-xxxx.onrender.com/api/v1/health> → `{"status":"ok"}`
- <https://agroai-api-xxxx.onrender.com/docs> → Swagger UI

Log in with the seeded demo account:

```text
Email:    ramesh@agrofield.ai
Password: Password123!
```

Then test **Crop Scanner**, **Scan History** and the profile photo upload.

> Change the demo password (or remove the demo account) before sharing a
> public production link.

---

## Updating the deployment

Every push to `main` triggers an automatic Render redeploy:

```powershell
git add .
git commit -m "Update app"
git push
```

---

## Free-plan limitations

| Item | Behaviour |
|---|---|
| Sleep | The free instance sleeps after ~15 minutes of inactivity. The first request may take 30–60 seconds. |
| SQLite database | Lives inside the container. Redeploys and some restarts reset users/scans. |
| Uploaded images | Stored in `backend/uploads/` inside the container; lost on redeploy. |
| Memory | 512 MB. The MobileNet model normally fits, but if the service crashes, upgrade to a paid instance. |

For persistent data, add a Render persistent disk (paid) or move the database
to Postgres/Neon and uploads to S3/Cloudinary.

---

## Troubleshooting

**The service crashes during build**
- Check the Render build logs. The PyTorch CPU wheel download can take a few
  minutes; a timeout on the first build is usually temporary — retry the deploy.

**The service starts but the page shows an old version**
- Hard-refresh with `Ctrl + F5`. Render may serve a cached `index.html`.

**`/api/v1/health` returns 502 or times out**
- The free instance is waking up. Wait 30–60 seconds and retry.
- Check the Render logs for a model-loading or database error.

**Login/register fails**
- Confirm the Render service is healthy.
- CORS is already open (`allow_origins=["*"]`), and the frontend uses the same
  origin by default.

**Images do not load**
- `/uploads/*` is served by the same FastAPI service. Check the Render logs and
  confirm the upload directory is writable.

**Vercel**
- This deployment intentionally does **not** use Vercel. Vercel's serverless
  functions cannot hold the PyTorch model (size limit) or a persistent SQLite
  database.

---

## Local development (unchanged)

```powershell
.\start.bat
```

- Frontend: <http://localhost:8080/>
- Backend: <http://127.0.0.1:8000/docs>

Or serve the combined app locally with:

```powershell
.\backend\.venv\Scripts\uvicorn.exe backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Then open <http://127.0.0.1:8000/>.
