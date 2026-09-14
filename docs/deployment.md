# Full-Stack Deployment Guide: AI Study Companion

This guide explains how to deploy the entire full-stack application (PostgreSQL + pgvector, FastAPI Backend, and Next.js Frontend) to production for **free** using **Neon**, **Render**, and **Vercel**.

---

## 1. Prerequisites Check
* **Database**: Already deployed on [Neon.tech](https://neon.tech) with `pgvector` enabled!
* **GitHub Repository**: Linked to `https://github.com/Gunda-nikhil919/lenny-growth-assistant`

---

## 2. Step 1: Push Changes to GitHub

Run these commands in your project root:
```powershell
git add .
git commit -m "feat: complete full-stack AI Study Companion implementation with pgvector and Neon DB"
git push origin main
```

---

## 3. Step 2: Deploy Backend to Render (Free)

1. Open [Render.com](https://render.com) and Sign In with **GitHub**.
2. Click **New +** at the top right and select **Web Service**.
3. Choose your repository: `Gunda-nikhil919/lenny-growth-assistant`.
4. Configure the service:
   * **Name**: `ai-study-companion-backend`
   * **Region**: `Ohio (US East)` (same as your Neon database for lowest latency)
   * **Root Directory**: `backend`
   * **Environment**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   * **Instance Type**: `Free`
5. Scroll down to **Environment Variables** and add:
   * `DATABASE_URL`: `postgresql+asyncpg://neondb_owner:npg_kPWXhY74dmJH@ep-red-glade-ayl3bdrs.c-5.us-east-2.aws.neon.tech/neondb`
   * `REDIS_URL`: `redis://localhost:6379/0` (or free cloud Redis from [Upstash.com](https://upstash.com))
   * `JWT_SECRET`: `super-secret-production-jwt-key-2026`
   * `ENVIRONMENT`: `production`
   * `OPENAI_API_KEY`: *(Optional: your OpenAI key if available)*
6. Click **Create Web Service**.
7. In ~2 minutes, Render will provide a live backend URL:  
   👉 `https://ai-study-companion-backend.onrender.com`

---

## 4. Step 3: Deploy Frontend to Vercel (Free)

1. Open [Vercel.com](https://vercel.com) and Sign In with **GitHub**.
2. Click **Add New...** → **Project**.
3. Select `Gunda-nikhil919/lenny-growth-assistant` and click **Import**.
4. Configure:
   * **Framework Preset**: `Next.js`
   * **Root Directory**: Click **Edit** and select `frontend`.
5. Under **Environment Variables**, add:
   * **Key**: `NEXT_PUBLIC_API_URL`
   * **Value**: Your Render Backend URL (e.g. `https://ai-study-companion-backend.onrender.com`)
6. Click **Deploy**.
7. In ~1 minute, your full-stack app is publicly accessible:  
   👉 `https://ai-study-companion.vercel.app`
