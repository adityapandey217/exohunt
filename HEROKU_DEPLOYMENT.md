# Heroku Deployment Guide

This guide will help you deploy the ExoHunt backend to Heroku.

## Prerequisites

- Heroku CLI installed and logged in (`heroku login`)
- Git repository initialized
- Python 3.13.1

## Step 1: Create Heroku App

```bash
# Navigate to project root
cd /Users/bimalsilwal/programming/exohunt

# Create a new Heroku app (replace 'your-app-name' with your desired name)
heroku create your-app-name

# Or let Heroku generate a random name
heroku create
```

## Step 2: Add Buildpacks

```bash
# Add Python buildpack
heroku buildpacks:add heroku/python
```

## Step 3: Set Environment Variables

```bash
# Generate a secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Set environment variables
heroku config:set SECRET_KEY='your-generated-secret-key'
heroku config:set DJANGO_SETTINGS_MODULE=exodetect.settings_prod
heroku config:set DEBUG=False
heroku config:set FRONTEND_URL=https://your-frontend-url.web.app

# Optional: Set Python version
heroku config:set PYTHON_RUNTIME_VERSION=3.13.1
```

## Step 4: Add PostgreSQL Database (Optional but Recommended)

```bash
# Add Heroku Postgres (free tier)
heroku addons:create heroku-postgresql:essential-0

# Database URL will be automatically set as DATABASE_URL
```

## Step 5: Deploy to Heroku

```bash
# Add all files to git
git add .
git commit -m "Prepare for Heroku deployment"

# Push to Heroku
git push heroku main

# If your branch is not 'main', use:
# git push heroku your-branch-name:main
```

## Step 6: Run Migrations

```bash
# Run database migrations
heroku run python exodetect/manage.py migrate

# Create superuser (optional)
heroku run python exodetect/manage.py createsuperuser

# Collect static files
heroku run python exodetect/manage.py collectstatic --noinput
```

## Step 7: Scale Web Dyno

```bash
# Ensure at least one web dyno is running
heroku ps:scale web=1
```

## Step 8: Open Your App

```bash
# Open in browser
heroku open

# Or visit the API directly
# https://your-app-name.herokuapp.com/api/
```

## Step 9: View Logs

```bash
# View real-time logs
heroku logs --tail

# View specific number of lines
heroku logs -n 200
```

## Important Notes

### File Storage

⚠️ **Heroku has ephemeral filesystem** - uploaded files (FITS, media) will be deleted on dyno restart!

**Solutions:**
1. Use **AWS S3** for file storage (recommended)
2. Use **Cloudinary** for media files
3. Configure **django-storages** with S3

Add to requirements.txt:
```
django-storages==1.14.4
boto3==1.35.99
```

### Model Files

The ML model files (`exoplanet_hybrid.pth`, `koi_scaler.joblib`, etc.) in `training/` directory should be committed to git since they're needed for predictions.

### Large Files

If model files are too large (>50MB), consider:
1. Using Git LFS (Large File Storage)
2. Hosting models on S3 and downloading on startup
3. Using Heroku's larger slug size (contact support)

### Dataset Files

The `dataset/koi.csv` and `lightcurves/*.fits` files:
- Keep `koi.csv` (small, ~2MB)
- Keep `example_lightcurves/*.fits` (9 files, 2.6MB total)
- Remove large `lightcurves/` directory (use `.slugignore`)

## Create .slugignore (Heroku's .gitignore)

```bash
cat > .slugignore << 'EOF'
*.md
*.ipynb
*.log
tests/
.vscode/
.git/
lightcurves/
training/lc_cache_npy/
training/features_cache_fits_only/
frontend/
.firebaserc
firebase.json
EOF
```

## Update CORS Settings

After deploying frontend to Firebase, update the environment variable:

```bash
heroku config:set FRONTEND_URL=https://your-app.web.app
```

## Troubleshooting

### Error: Application Error
```bash
# Check logs
heroku logs --tail

# Check config
heroku config
```

### Error: No module named 'X'
```bash
# Ensure package is in requirements.txt
# Re-deploy
git commit --allow-empty -m "Rebuild"
git push heroku main
```

### Error: Static files not found
```bash
# Collect static files
heroku run python exodetect/manage.py collectstatic --noinput
```

### Database Issues
```bash
# Reset database (CAUTION: Deletes all data)
heroku pg:reset DATABASE_URL
heroku run python exodetect/manage.py migrate
```

## Monitoring

```bash
# Check dyno status
heroku ps

# View app info
heroku info

# Check database info
heroku pg:info
```

## Cost Optimization

- **Eco Dyno**: $5/month (sleeps after 30 min of inactivity)
- **Essential Postgres**: $5/month (10GB storage)
- **Total**: ~$10/month for small apps

Free tier available with limitations.

## Next Steps

1. Deploy frontend to Firebase Hosting
2. Update `FRONTEND_URL` environment variable
3. Test API endpoints
4. Configure AWS S3 for file storage (if needed)
5. Set up monitoring and error tracking (e.g., Sentry)

## Quick Deploy Script

```bash
#!/bin/bash
# deploy.sh - Quick deployment script

# Commit changes
git add .
git commit -m "Deploy updates"

# Push to Heroku
git push heroku main

# Run migrations
heroku run python exodetect/manage.py migrate

# Restart dynos
heroku restart

echo "✅ Deployment complete!"
echo "Visit: https://$(heroku info -s | grep web_url | cut -d= -f2)"
```

Make executable: `chmod +x deploy.sh`

Run: `./deploy.sh`
