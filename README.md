# SportOase - IServ Buchungssystem

Ein vollständiges IServ-Modul für die Verwaltung und Buchung von Sportstunden.

## Übersicht

SportOase ist ein Buchungssystem, das vollständig in IServ integriert ist und IServs interne Benutzer- und Rechteverwaltung nutzt. Es ermöglicht Lehrkräften, Sportstunden zu buchen und Administratoren, Zeitslots zu blockieren.

## Features

- ✅ **Slot-Verwaltung**: Anzeige verfügbarer Zeitslots mit Echtzeitinformationen
- ✅ **Buchungssystem**: Einfache Buchung von Sportstunden für Klassen
- ✅ **Benutzerrechte**: Integration mit IServ-Berechtigungssystem (sportoase.user, sportoase.admin)
- ✅ **Admin-Panel**: Blockierung von Slots für Beratungsgespräche
- ✅ **Django Backend**: RESTful API mit Django und Django REST Framework
- ✅ **Angular Frontend**: Moderne, responsive Benutzeroberfläche
- ✅ **Docker-Ready**: Vollständige Docker-Konfiguration für Entwicklung und Deployment

## Architektur

### Backend (Django)
```
backend/
├── models.py           # Datenmodelle (Booking, TimeSlot, BlockedSlot, Notification)
├── services/
│   └── booking_service.py  # Business-Logik
├── views/
│   ├── slots.py        # Slot-Endpunkte
│   ├── bookings.py     # Buchungs-Endpunkte
│   └── admin.py        # Admin-Endpunkte
├── urls.py             # URL-Routing
├── settings.py         # Django-Konfiguration
└── manage.py           # Django Management
```

### Frontend (Angular)
```
frontend/src/app/
├── components/
│   ├── dashboard/      # Hauptseite
│   ├── slots/          # Slot-Übersicht
│   ├── booking-form/   # Buchungsformular
│   ├── my-bookings/    # Meine Buchungen
│   └── admin-panel/    # Admin-Verwaltung
├── services/
│   └── api.service.ts  # API-Kommunikation
└── app.module.ts       # Angular Hauptmodul
```

## Installation

### 1. IServ-Kompatibilität

Dieses Modul ist für IServ 3.x konzipiert und nutzt:
- IServ-Benutzer (`request.user`)
- IServ-Berechtigungen (`sportoase.user`, `sportoase.admin`)
- IServ-Datenbank (MariaDB/MySQL oder SQLite für Entwicklung)

### 2. Abhängigkeiten installieren

**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 3. Datenbank einrichten

```bash
python backend/manage.py migrate
python backend/manage.py createsuperuser
```

### 4. Beispiel-Zeitslots erstellen

```python
python backend/manage.py shell

from backend.models import TimeSlot
from datetime import time

# Erstelle Standard-Zeitslots
slots = [
    {'weekday': 'Mon', 'period': 1, 'label': '1. Stunde', 'start_time': time(8, 0), 'end_time': time(8, 45)},
    {'weekday': 'Mon', 'period': 2, 'label': '2. Stunde', 'start_time': time(8, 50), 'end_time': time(9, 35)},
    {'weekday': 'Mon', 'period': 3, 'label': '3. Stunde', 'start_time': time(9, 55), 'end_time': time(10, 40)},
    {'weekday': 'Mon', 'period': 4, 'label': '4. Stunde', 'start_time': time(10, 45), 'end_time': time(11, 30)},
    {'weekday': 'Mon', 'period': 5, 'label': '5. Stunde', 'start_time': time(11, 50), 'end_time': time(12, 35)},
    {'weekday': 'Mon', 'period': 6, 'label': '6. Stunde', 'start_time': time(12, 40), 'end_time': time(13, 25)},
]

# Für jeden Wochentag wiederholen
weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
for wd in weekdays:
    for s in slots:
        TimeSlot.objects.get_or_create(
            weekday=wd,
            period=s['period'],
            defaults={
                'label': s['label'],
                'start_time': s['start_time'],
                'end_time': s['end_time'],
                'max_students': 200
            }
        )
```

### 5. Rechte vergeben

In der IServ-Admin-Oberfläche:
1. Navigieren Sie zu **Benutzer & Gruppen** → **Berechtigungen**
2. Weisen Sie `sportoase.user` allen Lehrkräften zu
3. Weisen Sie `sportoase.admin` Administratoren zu

## Verwendung

### Für Lehrkräfte (sportoase.user)

1. **Dashboard**: Übersicht über das System
2. **Slots anzeigen**: Verfügbare Zeitslots für ein gewähltes Datum sehen
3. **Slot buchen**: 
   - Datum und Stunde auswählen
   - Angebotsart und -bezeichnung eingeben
   - Schüler hinzufügen
   - Buchung absenden
4. **Meine Buchungen**: Eigene Buchungen verwalten und löschen

### Für Administratoren (sportoase.admin)

Zusätzlich zu den Lehrkraft-Funktionen:
- **Slots blockieren**: Zeitslots für Beratungsgespräche oder andere Zwecke blockieren
- **Blockierte Slots verwalten**: Blockierungen aufheben
- **Alle Buchungen sehen**: Übersicht aller Buchungen im System

## API-Endpunkte

### Slots
- `GET /api/sportoase/slots?date=YYYY-MM-DD` - Verfügbare Slots abrufen
- `GET /api/sportoase/timeslots` - Alle konfigurierten Zeitslots

### Buchungen
- `POST /api/sportoase/book` - Neue Buchung erstellen
- `GET /api/sportoase/my-bookings` - Eigene Buchungen abrufen
- `GET /api/sportoase/bookings` - Alle Buchungen (Admin)
- `DELETE /api/sportoase/bookings/<id>` - Buchung löschen

### Admin
- `POST /api/sportoase/block-slot` - Slot blockieren (Admin)
- `POST /api/sportoase/unblock-slot` - Slot freigeben (Admin)
- `GET /api/sportoase/blocked-slots` - Blockierte Slots abrufen

## Entwicklung

### Backend-Server starten
```bash
python backend/manage.py runserver 0.0.0.0:8000
```

### Frontend-Server starten
```bash
cd frontend
npm start
```

Das Frontend läuft auf `http://localhost:4200` und kommuniziert mit dem Backend auf Port 8000.

## Docker-Deployment

```bash
docker-compose up -d
```

## Erweiterungen

### Neue Features hinzufügen

1. **Backend**: Erweitern Sie `backend/models.py`, `backend/services/booking_service.py` und Views
2. **Frontend**: Erstellen Sie neue Komponenten in `frontend/src/app/components/`
3. **API**: Fügen Sie neue Endpunkte in `backend/urls.py` hinzu

### Anpassungen

- **Zeitslots**: Ändern Sie die Zeitslots in der Datenbank oder `backend/settings.py`
- **Maximale Schüleranzahl**: Passen Sie `max_students` in den TimeSlot-Objekten an
- **Styling**: Bearbeiten Sie `frontend/src/styles.css` für Design-Anpassungen

## Technologie-Stack

- **Backend**: Django 4.2, Django REST Framework
- **Frontend**: Angular 15, TypeScript, Bootstrap 5
- **Datenbank**: SQLite (Entwicklung), MariaDB/MySQL (IServ-Produktion)
- **Deployment**: Docker, Nginx, Gunicorn

## Lizenz

Internes Modul für IServ-Installation

## Support

Bei Fragen oder Problemen wenden Sie sich an das SportOase-Team.
