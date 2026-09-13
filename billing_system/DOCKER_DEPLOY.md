# Docker Deployment Guide

Quick guide to deploy the Wi-Fi Billing System using Docker and Docker Compose.

## Prerequisites

- Docker installed and running
- Docker Compose installed
- Ports available: 5000 (Flask), 8501 (Streamlit), 3306 (MySQL)

## Quick Start

### 1. Navigate to Project Directory

```bash
cd billing_system
```

### 2. Create and Configure .env File

```bash
# Copy the example file
copy .env.example .env
```

**Edit `.env` and set strong passwords:**
```env
DB_PASSWORD=your-strong-password-here
SECRET_KEY=your-random-secret-key-here
JWT_SECRET_KEY=your-random-jwt-key-here
FLASK_ENV=production
```

> **Important**: Change `DB_PASSWORD`, `SECRET_KEY`, and `JWT_SECRET_KEY` from defaults!

### 3. Start All Services

```bash
# Build and start all containers
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 4. Access Services

| Service | URL | Purpose |
|---------|-----|---------|
| **Web App** | http://localhost:5000 | Register, login, dashboard |
| **API** | http://localhost:5000/api | REST API endpoints |
| **Dashboard** | http://localhost:8501 | Streamlit analytics |
| **MySQL** | localhost:3306 | Database (internal) |

### 5. Verify Health

```bash
# Check if services are healthy
curl http://localhost:5000/api/health

# Should return:
# {"status": "healthy", "database": "connected"}
```

## Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f db
docker-compose logs -f dashboard
```

### Stop Services
```bash
docker-compose down
```

### Stop and Remove Data
```bash
docker-compose down -v
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild Images
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Access Database
```bash
docker exec -it wifi-billing-db mysql -u wifiadmin -p wifi_billing
# Enter password when prompted
```

## Testing Deployment

### 1. Health Check
```bash
curl http://localhost:5000/api/health
```

### 2. Register User
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123456"
  }'
```

### 3. Check Web Interface
1. Open http://localhost:5000 in browser
2. Click "Register"
3. Fill in credentials
4. Click "Login"

### 4. Check Streamlit Dashboard
1. Open http://localhost:8501
2. Verify charts and metrics load

## Troubleshooting

### "Connection refused" to MySQL
```bash
# Check if db service is running
docker-compose ps

# Check db logs
docker-compose logs db

# Restart db service
docker-compose restart db
```

### "Port already in use"
```bash
# Find what's using port 5000
netstat -ano | findstr :5000

# Or change port in docker-compose.yml
# Change "5000:5000" to "5001:5000"
```

### "database connection failed"
```bash
# Verify DB is healthy
docker-compose exec db mysqladmin ping -u wifiadmin -p

# Check environment variables
docker-compose config | grep DB_
```

### Services not starting
```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

## Production Checklist

- [ ] Changed `DB_PASSWORD` in .env
- [ ] Changed `SECRET_KEY` in .env
- [ ] Changed `JWT_SECRET_KEY` in .env
- [ ] Set `FLASK_ENV=production`
- [ ] All services healthy (docker-compose ps)
- [ ] Can register user at http://localhost:5000/register
- [ ] Can login user at http://localhost:5000/login
- [ ] API health check returns healthy
- [ ] Streamlit dashboard loads

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| FLASK_ENV | production | Flask environment |
| DB_HOST | db | Database hostname |
| DB_USER | wifiadmin | Database user |
| DB_PASSWORD | wifi_password | Database password (CHANGE THIS!) |
| DB_NAME | wifi_billing | Database name |
| DB_PORT | 3306 | Database port |
| SECRET_KEY | - | Flask secret (GENERATE RANDOM!) |
| JWT_SECRET_KEY | - | JWT secret (GENERATE RANDOM!) |

## Scaling & Advanced

### Scale Backend Service
```bash
docker-compose up -d --scale backend=3
```

### Monitor Resource Usage
```bash
docker stats
```

### Backup Database
```bash
docker exec wifi-billing-db mysqldump -u wifiadmin -p wifi_billing > backup.sql
```

### Restore Database
```bash
docker exec -i wifi-billing-db mysql -u wifiadmin -p wifi_billing < backup.sql
```

## Next Steps

1. Test all functionality via web interface
2. Check Streamlit dashboard for analytics
3. Review logs for any warnings
4. Set up automated backups
5. Configure production reverse proxy (Nginx)
6. Enable HTTPS/SSL

## Support

- Check logs: `docker-compose logs`
- Review config: `docker-compose config`
- Verify health: `curl http://localhost:5000/api/health`
- Check database: `docker exec -it wifi-billing-db mysql -u wifiadmin -p wifi_billing -e "SHOW TABLES;"`

---

**For detailed information, see README.md and DEPLOYMENT.md**
