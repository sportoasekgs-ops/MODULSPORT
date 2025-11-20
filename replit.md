# SportOase - IServ Sports Facility Booking Module

## Project Overview
SportOase is a complete IServ module for booking sports facilities (e.g., gym halls) within schools. Built with Django backend and Angular frontend, it integrates seamlessly into IServ's platform using native authentication and permissions.

**Status**: IServ-only architecture complete, all security verified, ready for deployment testing

## Architecture

### Backend (Django)
- **Framework**: Django 4.2.7 with Django REST Framework
- **Database**: SQLite (development), MariaDB-compatible models for production IServ
- **Authentication**: Uses IServ's native `request.user` system (no separate user database)
- **Permissions**: 
  - `sportoase.user` - Teachers can book available slots
  - `sportoase.admin` - Administrators can block slots and view all bookings

### Frontend (Angular)
- **Framework**: Angular 17
- **Routing**: Five main views (Dashboard with Week Overview, Slots, Bookings, My Bookings, Admin)
- **Security**: CSRF tokens with withCredentials for all API calls
- **Authentication**: IServ-only (no separate login system)

### Models
1. **TimeSlot** - Defines available booking periods (day + period number)
2. **Booking** - Links user to timeslot with purpose and teacher info
3. **BlockedSlot** - Administrative blocks for maintenance/events
4. **Notification** - System notifications for administrators

## Recent Changes (November 20, 2025)

### IServ-First Architecture Update (Latest)
**Status**: Fully restructured for IServ-only authentication

**Major Changes**:
1. **Removed Separate Login System**
   - Deleted login component - authentication is exclusively through IServ
   - Frontend has no login UI - app starts directly on dashboard
   - Development API endpoints remain for testing purposes (not accessible via UI)

2. **Dashboard with Integrated Week Overview**
   - Dashboard is now the home page showing weekly overview directly
   - Full calendar-style grid displaying Monday through Friday
   - Each day shows all 6 periods with current status
   - Color-coded slots: Green (available), Yellow (almost full), Red (blocked)
   - Progress bars showing booking capacity
   - Navigation: Previous Week, Current Week, Next Week buttons
   - Click any slot to navigate directly to booking form
   - Quick access buttons to "Meine Buchungen" and "Admin"

3. **Admin Course Name Management**
   - Admins can now rename TimeSlot labels (course names)
   - New admin panel section: "Kursnamen verwalten"
   - Inline editing of course names with save/cancel
   - Backend API: `PUT /api/sportoase/timeslots/<id>` to update labels
   - Admin-only permission check (sportoase.admin required)
   - CSRF protection enabled for security

4. **API Endpoints**:
   - `GET /api/sportoase/slots/week?start_date=YYYY-MM-DD` - Week overview data
   - `GET /api/sportoase/timeslots` - Get all configured timeslots
   - `PUT /api/sportoase/timeslots/<id>` - Update timeslot label (admin only)

**IServ Authentication**:
- Authentication handled exclusively by IServAuthMiddleware
- Reads user info from IServ headers (X-IServ-User, X-IServ-Email, etc.)
- Auto-creates/updates Django user objects
- Syncs IServ groups to permissions:
  - `lehrer`/`teachers` → `sportoase.user`
  - `admin`/`administrators` → `sportoase.admin`
- Enabled via environment variable: `ISERV_AUTH_ENABLED=True`

**Files Modified**:
- `frontend/src/app/components/dashboard/dashboard.component.ts` - Integrated week overview
- `frontend/src/app/components/admin-panel/admin-panel.component.ts` - Added course management
- `frontend/src/app/app.module.ts` - Removed login, updated routing to dashboard
- `backend/views/slots.py` - Added update_timeslot_label endpoint
- `backend/urls.py` - Added timeslot update route
- `frontend/src/app/services/api.service.ts` - Added updateTimeslotLabel method

**Files Removed**:
- `frontend/src/app/components/login/` - Login component deleted

### IServ Production Deployment Configuration
**Status**: Ready for live IServ deployment

**New Files Added**:
1. `backend/settings_prod.py` - Production Django settings with MariaDB support
2. `backend/middleware/iserv_auth.py` - IServ authentication middleware
3. `deploy_iserv.sh` - Automated deployment script
4. `README_DEPLOYMENT.md` - Comprehensive deployment guide
5. `.env.example` - Environment configuration template

**Configuration Features**:
- **Database**: MariaDB/MySQL support for production IServ environments
- **Authentication**: IServ native auth integration via middleware
- **Security**: Production-ready HTTPS, secure cookies, CSRF protection
- **Deployment**: Automated build script and systemd service configuration
- **Frontend**: Angular production build with `/sportoase/` base path

**Environment Variables**:
The application now supports full environment-based configuration for IServ deployment, including database settings, domain configuration, and security options.

**Deployment Process**:
1. Run `./deploy_iserv.sh` to build production package
2. Copy to IServ server
3. Configure environment variables
4. Run migrations and collect static files
5. Configure Apache proxy and systemd service

See `README_DEPLOYMENT.md` for complete deployment instructions.

### Critical Security Fix - CSRF Protection
**Problem**: Initial implementation had `@csrf_exempt` decorators on all state-changing endpoints, creating a critical security vulnerability.

**Solution Implemented**:
1. Removed all `@csrf_exempt` decorators from views (create_booking, delete_booking, block_slot, unblock_slot, mark_notification_read)
2. Added CSRF token endpoint: `GET /api/sportoase/csrf`
3. Updated Angular API service to fetch and attach CSRF tokens to all requests
4. Added `withCredentials: true` to all HTTP calls for cookie transmission
5. Configured Django settings:
   - `CSRF_COOKIE_HTTPONLY = True`
   - `CSRF_COOKIE_SAMESITE = 'Lax'`
   - `CORS_ALLOW_CREDENTIALS = True`
   - Proper CORS and CSRF trusted origins

**Verification**: Architect review confirmed all CSRF vulnerabilities resolved and implementation is production-ready.

## Project Structure

```
/
├── backend/
│   ├── models.py              # Django ORM models
│   ├── settings.py            # Django configuration
│   ├── main_urls.py           # Root URL configuration
│   ├── urls.py                # SportOase API routes
│   ├── views/
│   │   ├── slots.py           # Slot availability views (incl. week overview)
│   │   ├── bookings.py        # Booking CRUD operations
│   │   ├── admin.py           # Admin blocking and notifications
│   │   ├── csrf.py            # CSRF token endpoint
│   │   └── auth.py            # Development authentication endpoints
│   ├── services/
│   │   └── booking_service.py # Business logic layer
│   ├── manage.py              # Django management
│   └── init_data.py           # Creates 30 initial timeslots
├── frontend/
│   └── src/app/
│       ├── components/
│       │   ├── dashboard/         # Main dashboard
│       │   ├── week-overview/     # Week calendar view
│       │   ├── slots/             # Slot browser
│       │   ├── booking-form/      # Create bookings
│       │   ├── my-bookings/       # User's bookings
│       │   ├── admin-panel/       # Admin tools
│       │   └── login/             # Dev login (testing only)
│       └── services/
│           └── api.service.ts # HTTP client with CSRF handling
├── module.json                # IServ module configuration
└── db.sqlite3                 # Development database
```

## API Endpoints

### Public Endpoints
- `GET /api/sportoase/csrf` - Get CSRF token
- `GET /api/sportoase/slots?date=YYYY-MM-DD` - Available slots for specific date
- `GET /api/sportoase/slots/week?start_date=YYYY-MM-DD` - Week overview (Monday-Friday)
- `GET /api/sportoase/timeslots` - All timeslots

### Development Endpoints (for local testing only)
- `POST /api/sportoase/login` - Login with username/password
- `POST /api/sportoase/logout` - Logout current user
- `GET /api/sportoase/check-auth` - Check authentication status

### User Endpoints (requires sportoase.user)
- `POST /api/sportoase/book` - Create booking
- `GET /api/sportoase/my-bookings` - User's bookings
- `DELETE /api/sportoase/bookings/{id}` - Delete own booking

### Admin Endpoints (requires sportoase.admin)
- `POST /api/sportoase/block-slot` - Block a timeslot
- `POST /api/sportoase/unblock-slot` - Unblock a timeslot
- `GET /api/sportoase/blocked-slots` - List blocked slots
- `GET /api/sportoase/bookings` - All bookings
- `GET /api/sportoase/notifications` - System notifications

## Initial Data
The database comes pre-populated with 30 timeslots:
- **Days**: Monday through Friday
- **Periods**: 1-6 (08:00-13:35)
- Configured in `backend/settings.py` under `PERIOD_TIMES`

## Development Environment
- **Workflow**: Django Backend running on `0.0.0.0:5000`
- **Database**: SQLite at `db.sqlite3`
- **Migrations**: Applied and up-to-date

## Deployment to IServ

### Quick Start

```bash
# 1. Build the deployment package
./deploy_iserv.sh

# 2. Transfer to IServ server
scp -r build/ admin@your-school.iserv.de:/tmp/sportoase

# 3. Follow detailed instructions in README_DEPLOYMENT.md
```

### Key Configuration Files

- **`backend/settings_prod.py`**: Production Django settings
- **`.env.example`**: Environment variable template
- **`deploy_iserv.sh`**: Automated deployment build script
- **`README_DEPLOYMENT.md`**: Complete deployment guide with:
  - Database setup (MariaDB)
  - Apache/Nginx proxy configuration
  - Systemd service setup
  - IServ authentication integration
  - Troubleshooting guide

### Environment Variables (Production)

```bash
ISERV_DOMAIN=your-school.iserv.de
ISERV_AUTH_ENABLED=True
DJANGO_SETTINGS_MODULE=backend.settings_prod
DB_ENGINE=mysql
DB_NAME=iserv_sportoase
DB_USER=sportoase
DB_PASSWORD=<secure-password>
DJANGO_SECRET_KEY=<secure-key>
DEBUG=False
HTTPS=True
```

### IServ Authentication

The middleware (`backend/middleware/iserv_auth.py`) integrates with IServ by:
- Reading IServ user headers (`X-IServ-User`, `X-IServ-Email`, etc.)
- Auto-creating/updating Django users
- Syncing IServ groups to Django permissions
- Mapping `lehrer`/`teachers` → `sportoase.user`
- Mapping `admin`/`administrators` → `sportoase.admin`

### Deployment Checklist

- [ ] Run `./deploy_iserv.sh` to create build package
- [ ] Copy build to IServ server
- [ ] Create MariaDB database and user
- [ ] Configure environment variables in `/etc/iserv/sportoase.env`
- [ ] Run migrations: `python backend/manage.py migrate --settings=backend.settings_prod`
- [ ] Initialize timeslots: `python backend/init_data.py`
- [ ] Configure Apache/Nginx proxy
- [ ] Set up systemd service
- [ ] Register IServ permissions: `sportoase.user` and `sportoase.admin`
- [ ] Test authentication and permissions
- [ ] Verify booking flow works end-to-end

## Security Features
- ✅ CSRF protection on all state-changing operations
- ✅ Django's built-in authentication via `request.user`
- ✅ IServ permission system integration
- ✅ Secure cookie handling with HttpOnly flags
- ✅ CORS configured for credential transmission
- ✅ No hardcoded credentials or secrets

## Known Limitations
- Currently configured for development (DEBUG=True, SQLite)
- Angular frontend needs to be built and served separately (not integrated into Django static files)
- Docker configuration pending (task 9 not yet started)

## Future Enhancements
- Docker containerization for easier deployment
- Email notifications for booking confirmations
- Recurring bookings (weekly patterns)
- Calendar view integration
- Conflict detection and warnings
