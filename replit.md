# SportOase - IServ Sports Facility Booking Module

## Project Overview
SportOase is a complete IServ module for booking sports facilities (e.g., gym halls) within schools. Built with Django backend and Angular frontend, it integrates seamlessly into IServ's platform using native authentication and permissions.

**Status**: Development complete, CSRF security verified, ready for deployment testing

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
- **Routing**: Five main views (Dashboard, Slots, Bookings, My Bookings, Admin)
- **Security**: CSRF tokens with withCredentials for all API calls

### Models
1. **TimeSlot** - Defines available booking periods (day + period number)
2. **Booking** - Links user to timeslot with purpose and teacher info
3. **BlockedSlot** - Administrative blocks for maintenance/events
4. **Notification** - System notifications for administrators

## Recent Changes (November 20, 2025)

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
│   │   ├── slots.py           # Slot availability views
│   │   ├── bookings.py        # Booking CRUD operations
│   │   ├── admin.py           # Admin blocking and notifications
│   │   └── csrf.py            # CSRF token endpoint
│   ├── services/
│   │   └── booking_service.py # Business logic layer
│   ├── manage.py              # Django management
│   └── init_data.py           # Creates 30 initial timeslots
├── frontend/
│   └── src/app/
│       ├── components/        # Angular UI components
│       └── services/
│           └── api.service.ts # HTTP client with CSRF handling
├── module.json                # IServ module configuration
└── db.sqlite3                 # Development database
```

## API Endpoints

### Public Endpoints
- `GET /api/sportoase/csrf` - Get CSRF token
- `GET /api/sportoase/slots?date=YYYY-MM-DD` - Available slots for date
- `GET /api/sportoase/timeslots` - All timeslots

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

## Deployment Checklist
Before deploying to production IServ:

1. **Environment Variables**:
   - Set `DEBUG=False`
   - Configure production database (MariaDB)
   - Update `SESSION_SECRET`

2. **Security Settings**:
   - Update `CSRF_TRUSTED_ORIGINS` with production hostname
   - Update `CORS_ALLOWED_ORIGINS` with production frontend URL
   - Set `CSRF_COOKIE_SECURE = True` (for HTTPS)
   - Set `SESSION_COOKIE_SECURE = True` (for HTTPS)

3. **Database**:
   - Run migrations against production database
   - Initialize timeslots via `python backend/init_data.py`

4. **IServ Integration**:
   - Copy module to IServ modules directory
   - Register permissions: `sportoase.user` and `sportoase.admin`
   - Verify menu integration in IServ interface

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
