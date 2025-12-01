# ASME Finance App - Deployment Guide

## Prerequisites
- GitHub account (or create one at github.com)
- Render.com account (free tier)
- Git installed on your computer

## Step 1: Initialize Git Repository Locally

```powershell
cd "c:\Users\spysa\OneDrive\Documents\ASME Finance 1"
git init
git config user.email "your.email@gmail.com"
git config user.name "Your Name"
git add .
git commit -m "Initial commit: ASME Finance App ready for deployment"
```

## Step 2: Create a New GitHub Repository

1. Go to **github.com** and sign in to your account
2. Click **+** icon (top right) → **New repository**
3. Fill in:
   - **Repository name:** `asme-finance` (or any name you prefer)
   - **Description:** "ASME Purdue Finance Management App"
   - **Visibility:** Choose "Public" or "Private"
   - **Initialize repository:** Leave unchecked (you already have local files)
4. Click **Create repository**

## Step 3: Connect Local Repo to GitHub

After creating the repo, GitHub will show commands. Copy the HTTPS URL, then run:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/asme-finance.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

**If you get authentication errors:**
- Generate a Personal Access Token:
  1. Go to GitHub Settings → Developer settings → Personal access tokens
  2. Click "Generate new token"
  3. Select `repo` scope, copy the token
  4. When git prompts for password, use the token instead

## Step 4: Deploy to Render

1. Go to **render.com** and sign up (use GitHub to sign up for easier connection)
2. Click **New +** → **Web Service**
3. Click **Connect repository** → Select your `asme-finance` repo
4. Fill in deployment settings:
   - **Name:** `asme-finance`
   - **Environment:** Python 3
   - **Region:** Choose closest to you
   - **Plan:** Free
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
5. Click **Create Web Service**

Render will automatically:
- Install dependencies from requirements.txt
- Create the database
- Seed the DesignTeam table
- Start your app

## Step 5: Access Your App

After deployment completes (takes 2-3 minutes):
- Your app will be available at `https://asme-finance.onrender.com`
- Share this URL with your team

## Updating Your App

To push new changes:

```powershell
git add .
git commit -m "Description of changes"
git push origin main
```

Render will automatically redeploy!

## Troubleshooting

**App won't start:**
- Check Render logs (in dashboard) for errors
- Ensure all imports in Python files are correct
- Verify all required packages are in requirements.txt

**Database not persisting:**
- SQLite on free tier may reset when app restarts
- For production, upgrade to PostgreSQL (also free on Render)

**File uploads not working:**
- Uploads stored locally won't persist on Render
- For production use, integrate cloud storage (AWS S3, etc.)

## Next Steps

- Share the Render URL with your ASME Finance team
- Start accepting real submissions
- Monitor app performance in Render dashboard
- Consider upgrading to paid tier if you need persistent storage
