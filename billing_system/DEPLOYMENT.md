# Deployment Guide

This guide covers various deployment options for the Wi-Fi Billing System.

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Production Server](#production-server)
4. [Cloud Platforms](#cloud-platforms)

## Local Development

### Windows Setup

1. **Install Python and MySQL**
   - Download Python from https://www.python.org/
   - Download MySQL from https://dev.mysql.com/downloads/mysql/

2. **Run Setup Script**
   ```bash
   cd billing_system
   setup.bat
   ```

3. **Configure Database**
   - Open MySQL Command Line or Workbench
   - Execute `models.sql`:
   ```bash
   mysql -u root -p < models.sql
   ```

4. **Update .env File**
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   ```

5. **Start Applications**
   ```bash
   # Terminal 1 - Flask Backend
   python app.py
   
   # Terminal 2 - Streamlit Dashboard
   streamlit run dashboard.py
   ```

### macOS/Linux Setup

1. **Install Python and MySQL**
   ```bash
   # Using Homebrew
   brew install python@3.9 mysql
   ```

2. **Run Setup Script**
   ```bash
   cd billing_system
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure Database**
   ```bash
   mysql -u root -p < models.sql
   ```

4. **Start Applications**
   ```bash
   # Terminal 1
   source venv/bin/activate
   python app.py
   
   # Terminal 2
   source venv/bin/activate
   streamlit run dashboard.py
   ```

## Docker Deployment

### Prerequisites
- Docker installed
- Docker Compose installed

### Quick Start

1. **Clone and Configure**
   ```bash
   cd billing_system
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **Build and Run**
   ```bash
   # Start all services
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
   ```

3. **Access Services**
   - Flask API: http://localhost:5000
   - Streamlit Dashboard: http://localhost:8501
   - MySQL: localhost:3306

### Docker Commands

```bash
# Stop all services
docker-compose down

# View running services
docker-compose ps

# View logs for specific service
docker-compose logs flask
docker-compose logs mysql
docker-compose logs streamlit

# Rebuild images
docker-compose build --no-cache

# Execute command in running container
docker-compose exec flask python -c "import app; print('OK')"
```

### Manual Docker Build

```bash
# Build Flask image
docker build -t wifi-billing-flask .

# Build Streamlit image
docker build -f Dockerfile.streamlit -t wifi-billing-streamlit .

# Run containers
docker run -p 5000:5000 --env-file .env wifi-billing-flask
docker run -p 8501:8501 --env-file .env wifi-billing-streamlit
```

## Production Server

### Using Gunicorn (Recommended)

1. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Run Flask Application**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app
   ```

3. **Using Systemd Service** (Linux)

   Create `/etc/systemd/system/wifi-billing.service`:
   ```ini
   [Unit]
   Description=Wi-Fi Billing System Flask App
   After=network.target

   [Service]
   Type=notify
   User=www-data
   WorkingDirectory=/var/www/wifi-billing-system/billing_system
   Environment="PATH=/var/www/wifi-billing-system/billing_system/venv/bin"
   ExecStart=/var/www/wifi-billing-system/billing_system/venv/bin/gunicorn \
       -w 4 -b 0.0.0.0:5000 --timeout 120 app:app
   Restart=on-failure
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable wifi-billing
   sudo systemctl start wifi-billing
   ```

### Using Nginx as Reverse Proxy

1. **Install Nginx**
   ```bash
   sudo apt-get install nginx
   ```

2. **Configure Nginx**

   Create `/etc/nginx/sites-available/wifi-billing`:
   ```nginx
   upstream flask_app {
       server 127.0.0.1:5000;
   }

   upstream streamlit_app {
       server 127.0.0.1:8501;
   }

   server {
       listen 80;
       server_name your-domain.com;

       # Flask API
       location /api/ {
           proxy_pass http://flask_app;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       # Static files
       location / {
           proxy_pass http://flask_app;
           proxy_set_header Host $host;
       }

       # Streamlit Dashboard
       location /dashboard/ {
           proxy_pass http://streamlit_app;
           proxy_set_header Host $host;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
   }
   ```

   Enable site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/wifi-billing /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### SSL/TLS with Let's Encrypt

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is enabled by default
sudo systemctl status certbot.timer
```

## Cloud Platforms

### Heroku Deployment

1. **Install Heroku CLI**
   ```bash
   curl https://cli.heroku.com/install.sh | sh
   ```

2. **Create Procfile** in root directory:
   ```
   web: cd billing_system && gunicorn -w 4 -b 0.0.0.0:$PORT app:app
   release: cd billing_system && python -c "import MySQLdb; print('DB OK')"
   ```

3. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

4. **Add MySQL Add-on**
   ```bash
   heroku addons:create jawsdb-mysql
   ```

5. **Set Environment Variables**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set JWT_SECRET_KEY=your-jwt-key
   ```

6. **Deploy**
   ```bash
   git push heroku main
   ```

### AWS Deployment

#### Using EC2

1. **Launch EC2 Instance**
   - Choose Ubuntu 20.04 LTS
   - Open ports 22, 80, 443, 5000, 8501

2. **Setup Server**
   ```bash
   sudo apt-get update
   sudo apt-get upgrade -y
   sudo apt-get install python3.9 python3-pip mysql-server nginx git -y
   ```

3. **Clone Repository**
   ```bash
   git clone your-repo-url
   cd billing_system
   ```

4. **Setup Application**
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with AWS RDS credentials
   ```

5. **Setup MySQL on RDS**
   - Create RDS MySQL instance
   - Update DB_HOST in .env to RDS endpoint
   - Run schema: `mysql -h <rds-endpoint> -u admin -p < models.sql`

6. **Setup Systemd Services** (see Production Server section)

### DigitalOcean Deployment

1. **Create Droplet**
   - Choose Ubuntu 20.04
   - Minimum 2GB RAM
   - Add SSH key

2. **Initial Setup**
   ```bash
   ssh root@your-droplet-ip
   apt-get update && apt-get upgrade -y
   apt-get install python3.9 python3-pip mysql-server nginx git -y
   ```

3. **Clone and Setup**
   ```bash
   git clone your-repo-url
   cd billing_system
   pip install -r requirements.txt
   ```

4. **Use DigitalOcean Managed Database**
   - Create MySQL database cluster
   - Update .env with connection details
   - Run schema

5. **Deploy with Nginx and Gunicorn** (see Production Server section)

### AWS Elastic Beanstalk

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize Application**
   ```bash
   cd billing_system
   eb init -p python-3.9 wifi-billing-system
   ```

3. **Create Procfile**
   ```
   web: gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

4. **Set Environment Variables**
   ```bash
   eb setenv DB_HOST=your-rds-endpoint DB_USER=admin DB_PASSWORD=password
   ```

5. **Deploy**
   ```bash
   eb create production-environment
   eb deploy
   ```

## Monitoring and Maintenance

### Application Monitoring

```bash
# Check Flask app status
curl http://localhost:5000/api/health

# View Gunicorn logs
journalctl -u wifi-billing -f

# Monitor system resources
top -p $(pgrep -f gunicorn)
```

### Database Maintenance

```bash
# Backup database
mysqldump -u root -p wifi_billing_system > backup.sql

# Restore database
mysql -u root -p wifi_billing_system < backup.sql

# Check database size
mysql -u root -p -e "SELECT table_name, ROUND(((data_length + index_length) / 1024 / 1024), 2) as size_mb FROM information_schema.tables WHERE table_schema = 'wifi_billing_system';"
```

### Log Management

```bash
# Flask logs
tail -f /var/log/wifi-billing/app.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# MySQL logs
tail -f /var/log/mysql/error.log
```

## Scaling Considerations

1. **Horizontal Scaling**: Run multiple Gunicorn workers
2. **Load Balancing**: Use Nginx or HAProxy
3. **Caching**: Implement Redis for session/data caching
4. **Database Optimization**: Add indexes, optimize queries
5. **CDN**: Use CloudFlare or AWS CloudFront for static assets

## Security Checklist

- [ ] Update SECRET_KEY and JWT_SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Enable database user authentication
- [ ] Implement rate limiting
- [ ] Enable CORS for trusted origins only
- [ ] Use environment variables for secrets
- [ ] Keep dependencies updated
- [ ] Enable logging and monitoring
- [ ] Set up intrusion detection
- [ ] Configure backup retention policy

## Troubleshooting

### 502 Bad Gateway
- Check Gunicorn service status
- Check Nginx configuration
- Review application logs

### Database Connection Timeouts
- Verify database server is running
- Check connection credentials in .env
- Check network connectivity
- Verify database user permissions

### High Memory Usage
- Reduce Gunicorn worker count
- Enable garbage collection
- Check for memory leaks in application
- Monitor with tools like Memray

### Slow Performance
- Check database query performance
- Enable query caching
- Add database indexes
- Use CDN for static files
- Enable gzip compression in Nginx

---

For more help, consult the main README.md and Flask documentation.
