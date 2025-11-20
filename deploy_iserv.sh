#!/bin/bash
# SportOase IServ Deployment Script
# This script prepares the SportOase module for deployment to IServ

set -e

echo "======================================"
echo "SportOase IServ Deployment Preparation"
echo "======================================"

# Configuration
ISERV_DOMAIN="${ISERV_DOMAIN:-your-school.iserv.de}"
ISERV_MODULE_DIR="${ISERV_MODULE_DIR:-/usr/share/iserv/modules/sportoase}"
BUILD_DIR="$(pwd)/build"

echo ""
echo "Configuration:"
echo "  IServ Domain: $ISERV_DOMAIN"
echo "  Module Directory: $ISERV_MODULE_DIR"
echo "  Build Directory: $BUILD_DIR"
echo ""

# Step 1: Install Python dependencies
echo "[1/6] Installing Python dependencies..."
pip install -r requirements.txt

# Step 2: Install mysqlclient for MariaDB support
echo "[2/6] Installing MySQL client for MariaDB..."
pip install mysqlclient

# Step 3: Install Node.js dependencies
echo "[3/6] Installing Node.js dependencies..."
cd frontend
npm install

# Step 4: Build Angular frontend for production
echo "[4/6] Building Angular frontend for production..."
npm run build -- --configuration production

# Step 5: Collect Django static files
echo "[5/6] Collecting Django static files..."
cd ../backend
export DJANGO_SETTINGS_MODULE=backend.settings_prod
export DB_ENGINE=sqlite
python manage.py collectstatic --noinput

# Step 6: Create deployment package
echo "[6/6] Creating deployment package..."
cd ..
mkdir -p "$BUILD_DIR"
cp -r backend "$BUILD_DIR/"
cp -r frontend/dist/sportoase-frontend "$BUILD_DIR/frontend_dist"
cp module.json "$BUILD_DIR/"
cp requirements.txt "$BUILD_DIR/"
cp README_DEPLOYMENT.md "$BUILD_DIR/"

echo ""
echo "======================================"
echo "Build Complete!"
echo "======================================"
echo ""
echo "Deployment package created in: $BUILD_DIR"
echo ""
echo "Next steps for IServ deployment:"
echo "  1. Copy $BUILD_DIR to your IServ server"
echo "  2. Set environment variables in IServ:"
echo "       - ISERV_DOMAIN=$ISERV_DOMAIN"
echo "       - DB_ENGINE=mysql"
echo "       - DB_NAME=iserv_sportoase"
echo "       - DB_USER=sportoase"
echo "       - DB_PASSWORD=<your-password>"
echo "       - DJANGO_SECRET_KEY=<your-secret-key>"
echo "       - DEBUG=False"
echo "       - HTTPS=True"
echo "       - ISERV_AUTH_ENABLED=True"
echo "  3. Run migrations: python backend/manage.py migrate --settings=backend.settings_prod"
echo "  4. Initialize data: python backend/init_data.py"
echo "  5. Configure IServ module permissions"
echo ""
echo "See README_DEPLOYMENT.md for detailed instructions."
echo ""
