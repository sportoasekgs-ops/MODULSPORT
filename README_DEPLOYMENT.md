# SportOase - IServ Deployment Guide

## Prerequisites

Before deploying SportOase to your IServ environment, ensure you have:

1. **IServ Server Access**: Administrator access to your IServ installation
2. **Database Access**: MariaDB/MySQL database for SportOase
3. **Python Environment**: Python 3.10+ installed on IServ
4. **Node.js**: Node.js 18+ for building the frontend (build server only)

## Deployment Steps

### 1. Prepare the Build

On your development machine or build server:

```bash
# Set your IServ domain
export ISERV_DOMAIN=your-school.iserv.de

# Run the deployment script
chmod +x deploy_iserv.sh
./deploy_iserv.sh
```

This creates a `build/` directory with all necessary files.

### 2. Transfer to IServ Server

Copy the build directory to your IServ server:

```bash
scp -r build/ admin@your-school.iserv.de:/tmp/sportoase
```

### 3. Configure IServ Environment

On the IServ server, set up environment variables in `/etc/iserv/sportoase.env`:

```bash
# IServ Configuration
ISERV_DOMAIN=your-school.iserv.de
ISERV_BASE_URL=https://your-school.iserv.de
ISERV_AUTH_ENABLED=True  # Set to True to enable IServ authentication middleware

# Django Configuration
DJANGO_SETTINGS_MODULE=backend.settings_prod
DJANGO_SECRET_KEY=<generate-a-secure-random-key>
DEBUG=False
HTTPS=True

# Database Configuration
DB_ENGINE=mysql
DB_NAME=iserv_sportoase
DB_USER=sportoase
DB_PASSWORD=<secure-database-password>
DB_HOST=localhost
DB_PORT=3306
```

**Generate a secure secret key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Create Database

On the IServ server, create the database and user:

```sql
CREATE DATABASE iserv_sportoase CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sportoase'@'localhost' IDENTIFIED BY 'your-secure-password';
GRANT ALL PRIVILEGES ON iserv_sportoase.* TO 'sportoase'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Install Python Dependencies

```bash
cd /tmp/sportoase
pip3 install -r requirements.txt
pip3 install mysqlclient gunicorn
```

### 6. Run Database Migrations

```bash
# Load environment variables
source /etc/iserv/sportoase.env

# Run migrations
python backend/manage.py migrate --settings=backend.settings_prod

# Initialize timeslots
python backend/init_data.py
```

### 7. Collect Static Files

```bash
python backend/manage.py collectstatic --noinput --settings=backend.settings_prod
```

### 8. Configure IServ Module

Copy the module to IServ's module directory:

```bash
sudo cp -r /tmp/sportoase /usr/share/iserv/modules/sportoase
sudo chown -R www-data:www-data /usr/share/iserv/modules/sportoase
```

### 9. Register Module with IServ

Add to IServ's module configuration (location varies by IServ version):

```json
{
  "id": "sportoase",
  "name": "SportOase",
  "enabled": true,
  "path": "/usr/share/iserv/modules/sportoase"
}
```

### 10. Configure Permissions

In IServ Admin Panel → System → Permissions:

1. Create permission group: `sportoase.user`
   - Assign to: Teachers, Students (as needed)
   - Description: "Can book sports facility slots"

2. Create permission group: `sportoase.admin`
   - Assign to: Administrators, Sports coordinators
   - Description: "Can manage SportOase and block slots"

### 11. Configure Web Server

#### Apache Configuration

Create `/etc/apache2/sites-available/sportoase.conf`:

```apache
<Location /sportoase>
    ProxyPass http://localhost:8001/sportoase
    ProxyPassReverse http://localhost:8001/sportoase
    
    # Pass IServ authentication headers
    RequestHeader set X-IServ-User %{ISERV_USER}e
    RequestHeader set X-IServ-Email %{ISERV_EMAIL}e
    RequestHeader set X-IServ-Firstname %{ISERV_FIRSTNAME}e
    RequestHeader set X-IServ-Lastname %{ISERV_LASTNAME}e
    RequestHeader set X-IServ-Groups %{ISERV_GROUPS}e
</Location>

<Location /api/sportoase>
    ProxyPass http://localhost:8001/api/sportoase
    ProxyPassReverse http://localhost:8001/api/sportoase
    
    # Pass IServ authentication headers
    RequestHeader set X-IServ-User %{ISERV_USER}e
    RequestHeader set X-IServ-Email %{ISERV_EMAIL}e
    RequestHeader set X-IServ-Firstname %{ISERV_FIRSTNAME}e
    RequestHeader set X-IServ-Lastname %{ISERV_LASTNAME}e
    RequestHeader set X-IServ-Groups %{ISERV_GROUPS}e
</Location>
```

Enable and reload:
```bash
sudo a2ensite sportoase
sudo systemctl reload apache2
```

### 12. Configure Systemd Service

Create `/etc/systemd/system/sportoase.service`:

```ini
[Unit]
Description=SportOase Gunicorn Service
After=network.target mariadb.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/usr/share/iserv/modules/sportoase
EnvironmentFile=/etc/iserv/sportoase.env

ExecStart=/usr/local/bin/gunicorn \
    --bind 127.0.0.1:8001 \
    --workers 4 \
    --worker-class sync \
    --timeout 60 \
    --log-file /var/log/sportoase/gunicorn.log \
    --access-logfile /var/log/sportoase/access.log \
    --error-logfile /var/log/sportoase/error.log \
    backend.wsgi:application

ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Create log directory:
```bash
sudo mkdir -p /var/log/sportoase
sudo chown www-data:www-data /var/log/sportoase
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable sportoase
sudo systemctl start sportoase
sudo systemctl status sportoase
```

### 13. Verify Deployment

1. **Check service status:**
   ```bash
   sudo systemctl status sportoase
   ```

2. **Check logs:**
   ```bash
   sudo tail -f /var/log/sportoase/gunicorn.log
   ```

3. **Test API endpoint:**
   ```bash
   curl https://your-school.iserv.de/api/sportoase/csrf
   ```

4. **Access frontend:**
   Navigate to: `https://your-school.iserv.de/sportoase`

### 14. Post-Deployment Configuration

1. **Create admin user** (if not using IServ auth):
   ```bash
   python backend/manage.py createsuperuser --settings=backend.settings_prod
   ```

2. **Verify permissions:**
   - Log in as a teacher → Should see booking interface
   - Log in as admin → Should see admin panel

3. **Test booking flow:**
   - Create a booking
   - Verify it appears in database
   - Test deletion
   - Test admin blocking features

## IServ Authentication Integration

SportOase integrates with IServ's authentication system through the `IServAuthMiddleware`. 

**Important**: The middleware is only activated when `ISERV_AUTH_ENABLED=True` is set in your environment variables. This allows the application to run in development mode (using standard Django auth) or production IServ mode.

This middleware:

1. Reads user information from IServ request headers
2. Automatically creates/updates Django users
3. Syncs IServ group memberships to Django permissions

### Required IServ Headers

Ensure your IServ installation passes these headers:

- `X-IServ-User`: Username
- `X-IServ-Email`: Email address
- `X-IServ-Firstname`: First name
- `X-IServ-Lastname`: Last name
- `X-IServ-Groups`: Comma-separated group list

### Permission Mapping

| IServ Group | Django Permission | Description |
|------------|-------------------|-------------|
| `lehrer`, `teachers` | `sportoase.user` | Can book slots |
| `admin`, `administrators` | `sportoase.admin` | Can manage system |

## Troubleshooting

### Database Connection Issues

```bash
# Test database connection
mysql -u sportoase -p iserv_sportoase -e "SHOW TABLES;"

# Check Django database connection
python backend/manage.py dbshell --settings=backend.settings_prod
```

### Service Won't Start

```bash
# Check detailed logs
sudo journalctl -u sportoase -n 50 --no-pager

# Test gunicorn manually
source /etc/iserv/sportoase.env
gunicorn --bind 127.0.0.1:8001 backend.wsgi:application
```

### Frontend Not Loading

1. Check static files are collected:
   ```bash
   ls -la /usr/share/iserv/modules/sportoase/staticfiles/
   ```

2. Verify Apache proxy configuration:
   ```bash
   sudo apache2ctl configtest
   ```

3. Check browser console for errors

### Authentication Not Working

1. Verify IServ headers are being passed:
   ```bash
   # Add to a view temporarily:
   print(request.META)
   ```

2. Check middleware is enabled in settings:
   ```python
   ISERV_AUTH_ENABLED = True
   ```

3. Verify permissions are created:
   ```bash
   python backend/manage.py shell --settings=backend.settings_prod
   >>> from django.contrib.auth.models import Permission
   >>> Permission.objects.filter(codename__in=['user', 'admin'])
   ```

## Backup and Maintenance

### Database Backup

```bash
# Create backup
mysqldump -u sportoase -p iserv_sportoase > sportoase_backup_$(date +%Y%m%d).sql

# Restore backup
mysql -u sportoase -p iserv_sportoase < sportoase_backup_20250120.sql
```

### Update Deployment

```bash
# Stop service
sudo systemctl stop sportoase

# Backup database
mysqldump -u sportoase -p iserv_sportoase > backup.sql

# Pull updates
cd /usr/share/iserv/modules/sportoase
git pull  # If using git

# Run migrations
python backend/manage.py migrate --settings=backend.settings_prod

# Collect static files
python backend/manage.py collectstatic --noinput --settings=backend.settings_prod

# Restart service
sudo systemctl start sportoase
```

### Log Rotation

Create `/etc/logrotate.d/sportoase`:

```
/var/log/sportoase/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload sportoase > /dev/null 2>&1 || true
    endscript
}
```

## Security Checklist

- [ ] `DEBUG = False` in production
- [ ] Secure `DJANGO_SECRET_KEY` generated and set
- [ ] Database password is strong and unique
- [ ] `HTTPS = True` for secure cookies
- [ ] CSRF trusted origins configured correctly
- [ ] File permissions set correctly (www-data:www-data)
- [ ] Firewall configured (only necessary ports open)
- [ ] Regular database backups configured
- [ ] Log rotation configured
- [ ] Security updates applied regularly

## Support

For issues or questions:

1. Check the logs: `/var/log/sportoase/`
2. Review IServ documentation: https://doku.iserv.de/
3. Check Django documentation: https://docs.djangoproject.com/

## License

SportOase is licensed under [Your License]. See LICENSE file for details.
