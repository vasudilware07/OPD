# Deployment Guide — Render (Backend) + Vercel (Frontend)

## Architecture

```
[Vercel]                    [Render]                [MongoDB Atlas]
Next.js Frontend  ──API──>  FastAPI Backend  ──DB──>  Cloud Database
(localhost:3000)            (localhost:8000)
```

---

## Step 1: Set Up MongoDB Atlas (Free Cloud Database)

Since Render doesn't include MongoDB, you need a free MongoDB Atlas cluster.

1. Go to [mongodb.com/atlas](https://www.mongodb.com/atlas) and create a free account
2. Click **"Build a Database"** → Choose **M0 Free Tier**
3. Select a region close to your Render region (e.g., **Mumbai** for Singapore)
4. Create a database user:
   - Username: `plumadmin`
   - Password: (generate a strong password, save it)
5. Under **Network Access**, click **"Add IP Address"** → **"Allow Access from Anywhere"** (0.0.0.0/0)
6. Click **"Connect"** → **"Connect your application"** → Copy the connection string:
   ```
   mongodb+srv://plumadmin:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
7. Replace `<password>` with your actual password

---

## Step 2: Deploy Backend on Render

### Option A: One-click from render.yaml (Recommended)

1. Go to [render.com](https://render.com) and sign in with GitHub
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub repo (`vasudilware07/OPD`)
4. Render will auto-detect the `render.yaml` file
5. Fill in the environment variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `MONGODB_URL`: Your MongoDB Atlas connection string from Step 1
   - `CORS_ORIGINS`: Your Vercel frontend URL (set after Step 3)
6. Click **"Apply"** — Render will build and deploy

### Option B: Manual Setup

1. Go to [render.com](https://render.com) → **"New"** → **"Web Service"**
2. Connect your GitHub repo
3. Configure:
   | Setting | Value |
   |---------|-------|
   | Name | `plum-claimguard-api` |
   | Region | Singapore (or closest) |
   | Runtime | Python 3 |
   | Build Command | `cd backend && pip install -r requirements.txt` |
   | Start Command | `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT` |
   | Plan | Free |

4. Add **Environment Variables**:
   | Key | Value |
   |-----|-------|
   | `GEMINI_API_KEY` | Your Gemini API key |
   | `MONGODB_URL` | `mongodb+srv://plumadmin:xxx@cluster0.xxx.mongodb.net/plum_opd` |
   | `DATABASE_NAME` | `plum_opd` |
   | `CORS_ORIGINS` | `https://your-frontend.vercel.app` (update after Vercel deploy) |
   | `PYTHON_VERSION` | `3.12.0` |

5. Click **"Create Web Service"**
6. Wait for build to complete (~3-5 minutes)
7. Your backend URL will be: `https://plum-claimguard-api.onrender.com`

### Seed the Database (One-time)

After deploying, seed the database by running this in your local terminal:
```bash
cd backend
# Update .env with your MongoDB Atlas URL
.\venv\Scripts\python.exe seed.py
```

Or add a one-time job on Render:
- Render Dashboard → Your service → **"Jobs"** tab → **"New Job"**
- Command: `cd backend && python seed.py`
- Run once

---

## Step 3: Deploy Frontend on Vercel

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click **"Add New Project"** → Import `vasudilware07/OPD`
3. Configure:
   | Setting | Value |
   |---------|-------|
   | Framework Preset | Next.js |
   | Root Directory | `frontend` |
   | Build Command | `npm run build` |
   | Output Directory | `.next` |

4. Add **Environment Variable**:
   | Key | Value |
   |-----|-------|
   | `NEXT_PUBLIC_API_URL` | `https://plum-claimguard-api.onrender.com` |

5. Click **"Deploy"**
6. Your frontend URL will be: `https://opd-xxx.vercel.app`

### IMPORTANT: Update Render CORS

After getting your Vercel URL, go back to Render:
1. Render Dashboard → Your service → **"Environment"**
2. Update `CORS_ORIGINS` to: `https://opd-xxx.vercel.app`
3. Click **"Save Changes"** — Render will auto-redeploy

---

## Step 4: Verify Deployment

1. Open your Vercel URL (frontend)
2. Check the dashboard loads with stats
3. Submit a test claim:
   - Go to `/claims/new`
   - Select a member
   - Upload a mock document from `sample_documents/`
   - Submit and verify AI adjudication works

---

## CI/CD Pipeline

The GitHub Actions pipeline (`.github/workflows/ci.yml`) runs on every push:

```
Push to main
    │
    ├── Backend CI
    │   ├── Install Python deps
    │   ├── Lint with ruff
    │   ├── Check imports
    │   └── Run rule engine tests
    │
    ├── Frontend CI
    │   ├── Install Node deps
    │   ├── ESLint
    │   └── Production build
    │
    └── Auto-deploy (if CI passes)
        ├── Render auto-deploys backend (GitHub integration)
        └── Vercel auto-deploys frontend (GitHub integration)
```

Both Render and Vercel watch the `main` branch and auto-deploy on push — no manual triggers needed once connected.

---

## Cost Summary

| Service | Plan | Cost |
|---------|------|------|
| Vercel (Frontend) | Hobby | Free |
| Render (Backend) | Free | Free (spins down after 15min idle) |
| MongoDB Atlas | M0 | Free (512MB storage) |
| Gemini API | Free tier | Free (1500 req/day) |
| **Total** | | **$0/month** |

> **Note**: Render's free tier spins down after 15 minutes of inactivity. The first request after idle takes ~30-60 seconds to cold-start. For production, upgrade to Render's $7/month plan.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| CORS errors | Ensure `CORS_ORIGINS` in Render matches your exact Vercel URL |
| MongoDB connection fails | Check Atlas IP whitelist includes 0.0.0.0/0 |
| Gemini API errors | Verify API key is valid and has quota remaining |
| Frontend shows "Cannot connect" | Check `NEXT_PUBLIC_API_URL` points to your Render URL |
| Render build fails | Check Python version is 3.12 and requirements.txt is correct |
| Vercel build fails | Ensure root directory is set to `frontend` |
