# Smart Wallet - Render.com Deployment Guide

## Prerequisites
- GitHub account
- Render.com account
- Your Smart Wallet code pushed to a GitHub repository

## Step-by-Step Deployment

### 1. Prepare Your Repository
Make sure your repository contains all the necessary files:
- `requirements.txt`
- `build.sh`
- `Procfile`
- `runtime.txt`
- `.env.example`
- Updated `settings.py` with environment variable support

### 2. Create a New Web Service on Render

1. Go to [Render.com](https://render.com) and sign in
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:

**Basic Settings:**
- **Name**: `smart-wallet` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn smart_wallet.wsgi:application`

### 3. Environment Variables

Add these environment variables in Render dashboard:

**Required Variables:**
```
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
DEBUG=False
ALLOWED_HOSTS=.render.com
DJANGO_LOG_LEVEL=INFO
```

**Security Variables (Optional but Recommended):**
```
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY
```

### 4. Database Setup

**Option A: PostgreSQL (Recommended for Production)**
1. Create a new PostgreSQL database on Render
2. Copy the `DATABASE_URL` from your database dashboard
3. Add `DATABASE_URL` to your web service environment variables

**Option B: SQLite (Development/Testing)**
- No additional setup needed
- Data will be reset on each deployment

### 5. Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Install dependencies
   - Run migrations
   - Create superuser (admin/admin123)
   - Create default categories
   - Collect static files
   - Start the application

### 6. Post-Deployment

1. **Access your application**: `https://your-app-name.onrender.com`
2. **Admin access**: `https://your-app-name.onrender.com/admin/`
   - Username: `admin`
   - Password: `admin123`
3. **Change admin password** immediately after first login

### 7. Custom Domain (Optional)

1. Go to your service settings
2. Add your custom domain
3. Configure DNS records as instructed

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Django secret key | - | Yes |
| `DEBUG` | Debug mode | False | No |
| `ALLOWED_HOSTS` | Allowed hostnames | .render.com | No |
| `DATABASE_URL` | Database connection | SQLite | No |
| `DJANGO_LOG_LEVEL` | Logging level | INFO | No |

## Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify `build.sh` has correct permissions

### Application Won't Start
- Check application logs
- Verify `ALLOWED_HOSTS` includes your Render domain
- Ensure `SECRET_KEY` is set

### Static Files Not Loading
- Verify `STATIC_ROOT` and `STATIC_URL` settings
- Check if `collectstatic` ran successfully in build logs

### Database Issues
- For PostgreSQL: Verify `DATABASE_URL` is correct
- Check migration logs in build process

## Security Checklist

- [ ] Changed default admin password
- [ ] Set strong `SECRET_KEY`
- [ ] Disabled `DEBUG` in production
- [ ] Configured HTTPS settings
- [ ] Set up proper `ALLOWED_HOSTS`
- [ ] Reviewed and set security headers

## Support

For issues specific to this application, check the application logs in your Render dashboard.
For Render-specific issues, consult the [Render documentation](https://render.com/docs).