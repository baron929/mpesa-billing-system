# Pre-Deployment Checklist for Docker

Complete this checklist before running `docker-compose up`

## System Requirements

- [ ] Docker installed: `docker --version`
- [ ] Docker Compose installed: `docker-compose --version`
- [ ] Docker daemon running (Docker Desktop open)
- [ ] At least 4GB RAM available
- [ ] At least 2GB disk space available
- [ ] Ports available: 5000, 8501, 3306

## Project Structure

- [ ] In directory: `c:\Users\baron\Mpesa-Based_Wi-Fi-Hotspot_Billing_System\billing_system\`
- [ ] File exists: `app.py`
- [ ] File exists: `dashboard.py`
- [ ] File exists: `Dockerfile`
- [ ] File exists: `Dockerfile.streamlit`
- [ ] File exists: `docker-compose.yml`
- [ ] File exists: `models.sql`
- [ ] File exists: `requirements.txt`
- [ ] Directory exists: `templates/`

## Configuration Files

- [ ] Created `.env` from `.env.example`
- [ ] Opened `.env` in editor
- [ ] Set unique `DB_PASSWORD` (changed from default)
- [ ] Set unique `SECRET_KEY` (not default value)
- [ ] Set unique `JWT_SECRET_KEY` (not default value)
- [ ] Set `FLASK_ENV=production` (for production) or `development` (for testing)
- [ ] Verified `DB_HOST=db` (for Docker)
- [ ] Verified `DB_USER=wifiadmin`
- [ ] Verified `DB_NAME=wifi_billing`

## Security

- [ ] All passwords are strong (mix of upper, lower, numbers, special chars)
- [ ] `SECRET_KEY` is random (at least 32 characters)
- [ ] `JWT_SECRET_KEY` is random (at least 32 characters)
- [ ] No passwords committed to git
- [ ] .env file is in .gitignore

## Docker Configuration

- [ ] docker-compose.yml has correct service names: `backend`, `db`, `dashboard`
- [ ] Dockerfile uses correct base image: `python:3.9-slim`
- [ ] Dockerfile.streamlit exists and is correct
- [ ] All volume paths are correct
- [ ] All port mappings are correct (5000:5000, 8501:8501, 3306:3306)
- [ ] Health checks configured

## Database Schema

- [ ] `models.sql` file exists
- [ ] File contains CREATE TABLE statements
- [ ] File contains indexes and foreign keys
- [ ] File is not too large (< 10KB)

## Python Dependencies

- [ ] `requirements.txt` exists
- [ ] Contains: Flask, flask-cors, mysql-connector-python, bcrypt, PyJWT
- [ ] Contains: Streamlit, pandas, plotly for dashboard
- [ ] Contains: gunicorn for production
- [ ] No broken or incompatible versions

## Application Code

- [ ] `app.py` imports all required modules
- [ ] `app.py` has Flask app definition
- [ ] `app.py` has all 7 API endpoints
- [ ] `dashboard.py` has Streamlit app definition
- [ ] No syntax errors in Python files

## Templates

- [ ] Directory `templates/` exists
- [ ] Contains `index.html`
- [ ] Contains `register.html`
- [ ] Contains `login.html`
- [ ] Contains `dashboard.html`
- [ ] All HTML files are valid

## Port Conflicts

- [ ] Port 5000 is not in use: `netstat -ano | findstr :5000`
- [ ] Port 8501 is not in use: `netstat -ano | findstr :8501`
- [ ] Port 3306 is not in use: `netstat -ano | findstr :3306`

## Terminal & Workspace

- [ ] PowerShell/Terminal open
- [ ] Current directory: `billing_system`
- [ ] Can run commands: `docker ps` should work
- [ ] Can write to directory: `dir` shows files

## Ready to Deploy?

**Pre-Deployment Summary:**
```
Total Checks: _____ / _____

✅ If ALL checked → Ready to deploy!
❌ If any unchecked → Fix issues first
```

## Deployment Commands

Once all checks pass, run:

```bash
# Navigate to billing_system
cd billing_system

# Build and start all services
docker-compose up -d --build

# Wait 20-30 seconds for services to start

# Verify all containers running
docker-compose ps

# Check backend health
curl http://localhost:5000/api/health

# View logs if needed
docker-compose logs -f
```

## Quick Verification

After deployment:

1. **Open Web Browser**
   - Go to: http://localhost:5000
   - Should see home page

2. **Test Registration**
   - Click "Register"
   - Create test account
   - Should see success message

3. **Test Login**
   - Use registered credentials
   - Should redirect to dashboard

4. **Check Streamlit**
   - Go to: http://localhost:8501
   - Should show analytics dashboard

5. **Test API**
   ```bash
   curl http://localhost:5000/api/health
   # Should return: {"status": "healthy", "database": "connected"}
   ```

## Troubleshooting During Deployment

**If services fail to start:**
```bash
# Check logs
docker-compose logs

# Check specific service
docker-compose logs db
docker-compose logs backend

# Restart
docker-compose restart
```

**If database won't connect:**
```bash
# Check db container is running
docker-compose ps

# Check db logs
docker-compose logs db

# Wait 30-40 seconds and retry
```

**If Python modules fail:**
```bash
# Rebuild with no cache
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Success Indicators

- [ ] All 3 containers running: `docker-compose ps`
- [ ] Backend responds: `curl http://localhost:5000/api/health`
- [ ] Web page loads: http://localhost:5000
- [ ] Registration works
- [ ] Login works
- [ ] Dashboard appears
- [ ] No errors in logs: `docker-compose logs`

---

**Date Checked:** ___________
**Checked By:** ___________
**Status:** ☐ Ready ☐ Issues Found

See DOCKER_DEPLOY.md for detailed commands and troubleshooting.
