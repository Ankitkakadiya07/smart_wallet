# 🔧 Render.com Deployment Troubleshooting Guide

## 🚨 Common Issues and Solutions

### Issue 1: psycopg2-binary Build Error
**Error**: `Getting requirements to build wheel did not run successfully`

**Solutions**:

#### Option A: Use SQLite (Recommended for MVP)
1. Use the current `requirements.txt` (without psycopg2)
2. Don't create a PostgreSQL database
3. Your app will use SQLite by default

#### Option B: Use PostgreSQL with Alternative Package
1. Create a PostgreSQL database on Render first
2. Use `requirements-render.txt` instead:
   ```bash
   # In Render dashboard, change build command to:
   pip install -r requirements-render.txt && ./build.sh
   ```

#### Option C: Manual Installation
1. Use `render-build.sh` as build command instead of `build.sh`
2. This script handles psycopg2 installation more gracefully

### Issue 2: Python Version Compatibility
**Error**: Package compatibility issues

**Solution**: 
- Updated `runtime.txt` to use Python 3.11.9
- This version has better package compatibility

### Issue 3: Static Files Not Loading
**Error**: CSS/JS files not found

**Solution**:
- Ensure `collectstatic` runs in build script
- Check `STATIC_ROOT` and `STATIC_URL` settings
- Verify WhiteNoise is in `MIDDLEWARE`

## 🚀 Deployment Options

### Option 1: SQLite Deployment (Simplest)
```bash
# Render Configuration:
Build Command: ./build.sh
Start Command: gunicorn smart_wallet.wsgi:application

# Environment Variables:
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=.render.com
```

### Option 2: PostgreSQL Deployment
```bash
# Render Configuration:
Build Command: ./render-build.sh
Start Command: gunicorn smart_wallet.wsgi:application

# Environment Variables:
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=.render.com
DATABASE_URL=postgresql://... (from Render PostgreSQL service)
```

### Option 3: Manual Requirements
```bash
# Render Configuration:
Build Command: pip install -r requirements-minimal.txt && ./build.sh
Start Command: gunicorn smart_wallet.wsgi:application
```

## 🔍 Debugging Steps

### 1. Check Build Logs
- Go to Render Dashboard → Your Service → Events
- Look for specific error messages
- Check which step is failing

### 2. Verify Environment Variables
- Ensure `SECRET_KEY` is set
- Check `ALLOWED_HOSTS` includes your domain
- Verify `DEBUG=False` for production

### 3. Test Locally
```bash
# Test with production settings
export DEBUG=False
export SECRET_KEY=test-key
python manage.py check --deploy
```

### 4. Check Dependencies
```bash
# Test requirements installation
pip install -r requirements.txt
```

## 🛠️ Alternative Deployment Methods

### Method 1: Fork and Modify
1. Fork the repository
2. Modify `requirements.txt` as needed
3. Deploy from your fork

### Method 2: Use Docker (Advanced)
Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "smart_wallet.wsgi:application"]
```

### Method 3: Use Railway or Heroku
- Railway.app has better Python 3.13 support
- Heroku has mature Django deployment

## 📞 Getting Help

### If Build Still Fails:
1. **Check Render Status**: [status.render.com](https://status.render.com)
2. **Try Different Python Version**: Change `runtime.txt` to `python-3.10.12`
3. **Use Minimal Setup**: Deploy with SQLite first, add PostgreSQL later
4. **Contact Support**: Render has excellent support for deployment issues

### Working Configuration (Guaranteed):
```
# runtime.txt
python-3.11.9

# requirements.txt (minimal)
Django==4.2.16
python-decouple==3.8
whitenoise==6.6.0
gunicorn==21.2.0
dj-database-url==2.1.0

# Environment Variables
SECRET_KEY=your-50-character-secret-key
DEBUG=False
ALLOWED_HOSTS=.render.com
```

## ✅ Success Checklist

- [ ] Python 3.11.9 in `runtime.txt`
- [ ] Minimal `requirements.txt` without psycopg2
- [ ] `SECRET_KEY` environment variable set
- [ ] `DEBUG=False` in environment
- [ ] `ALLOWED_HOSTS=.render.com` in environment
- [ ] Build command: `./build.sh`
- [ ] Start command: `gunicorn smart_wallet.wsgi:application`

## 🎯 Quick Fix Commands

```bash
# Update repository with fixes
git add .
git commit -m "Fix Render deployment issues"
git push origin main

# Then redeploy on Render
```

Your Smart Wallet should now deploy successfully! 🚀