import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-week-overview',
  template: `
    <div class="card">
      <h2>Wochenübersicht</h2>
      <p class="lead">Übersicht aller verfügbaren Slots für die Woche</p>
      
      <div class="week-controls mb-4">
        <button class="btn btn-secondary me-2" (click)="previousWeek()">
          ← Vorherige Woche
        </button>
        <button class="btn btn-secondary me-2" (click)="currentWeek()">
          Aktuelle Woche
        </button>
        <button class="btn btn-secondary" (click)="nextWeek()">
          Nächste Woche →
        </button>
        <span class="ms-3 text-muted">
          Woche ab {{ formatDate(startDate) }}
        </span>
      </div>
      
      <div *ngIf="loading" class="loading-container">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Laden...</span>
        </div>
      </div>
      
      <div *ngIf="!loading && weekData.length > 0" class="week-grid">
        <div *ngFor="let day of weekData" class="day-column">
          <div class="day-header">
            <h5>{{ getWeekdayName(day.weekday) }}</h5>
            <small class="text-muted">{{ formatDateShort(day.date) }}</small>
          </div>
          
          <div class="slots-container">
            <div *ngFor="let slot of day.slots" 
                 class="slot-card mb-2" 
                 [ngClass]="getSlotClass(slot)"
                 (click)="selectSlot(day.date, slot)">
              <div class="slot-header">
                <strong>{{ slot.period }}. Stunde</strong>
                <small>{{ slot.start_time }} - {{ slot.end_time }}</small>
              </div>
              <div class="slot-info">
                <div *ngIf="!slot.is_blocked">
                  <small>{{ slot.current_students }}/{{ slot.max_students }}</small>
                  <div class="progress mt-1" style="height: 4px;">
                    <div class="progress-bar" 
                         [ngClass]="getProgressClass(slot)"
                         [style.width.%]="getProgressPercent(slot)">
                    </div>
                  </div>
                </div>
                <div *ngIf="slot.is_blocked" class="text-danger">
                  <small><strong>Blockiert</strong></small>
                </div>
              </div>
              <div *ngIf="slot.bookings && slot.bookings.length > 0" class="mt-1">
                <small class="text-muted">
                  {{ slot.bookings[0].offer_label }}
                  <span *ngIf="slot.bookings.length > 1">
                    +{{ slot.bookings.length - 1 }}
                  </span>
                </small>
              </div>
            </div>
            
            <div *ngIf="day.slots.length === 0" class="alert alert-info">
              Keine Slots
            </div>
          </div>
        </div>
      </div>
      
      <div *ngIf="!loading && weekData.length === 0" class="alert alert-warning">
        Keine Daten für diese Woche verfügbar
      </div>
      
      <div *ngIf="errorMessage" class="alert alert-danger mt-3">
        {{ errorMessage }}
      </div>
    </div>
  `,
  styles: [`
    .week-grid {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 15px;
      margin-top: 20px;
    }
    
    @media (max-width: 1200px) {
      .week-grid {
        grid-template-columns: repeat(3, 1fr);
      }
    }
    
    @media (max-width: 768px) {
      .week-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }
    
    @media (max-width: 480px) {
      .week-grid {
        grid-template-columns: 1fr;
      }
    }
    
    .day-column {
      border: 1px solid #dee2e6;
      border-radius: 8px;
      overflow: hidden;
      background: white;
    }
    
    .day-header {
      background: linear-gradient(135deg, #2c5aa0 0%, #5a8ed9 100%);
      color: white;
      padding: 12px;
      text-align: center;
    }
    
    .day-header h5 {
      margin: 0;
      font-size: 1rem;
    }
    
    .day-header small {
      color: rgba(255, 255, 255, 0.9);
    }
    
    .slots-container {
      padding: 10px;
      max-height: 600px;
      overflow-y: auto;
    }
    
    .slot-card {
      padding: 10px;
      border-radius: 6px;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
      border: 1px solid #dee2e6;
    }
    
    .slot-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    .slot-card.slot-available {
      background-color: #d4edda;
      border-left: 4px solid #28a745;
    }
    
    .slot-card.slot-blocked {
      background-color: #f8d7da;
      border-left: 4px solid #dc3545;
      cursor: not-allowed;
    }
    
    .slot-card.slot-full {
      background-color: #fff3cd;
      border-left: 4px solid #ffc107;
    }
    
    .slot-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 5px;
    }
    
    .slot-header strong {
      font-size: 0.9rem;
    }
    
    .slot-header small {
      font-size: 0.75rem;
      color: #6c757d;
    }
    
    .slot-info {
      font-size: 0.85rem;
    }
    
    .progress-bar.bg-success {
      background-color: #28a745 !important;
    }
    
    .progress-bar.bg-warning {
      background-color: #ffc107 !important;
    }
    
    .progress-bar.bg-danger {
      background-color: #dc3545 !important;
    }
    
    .week-controls {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
    }
    
    .loading-container {
      min-height: 400px;
      display: flex;
      justify-content: center;
      align-items: center;
    }
  `]
})
export class WeekOverviewComponent implements OnInit {
  weekData: any[] = [];
  startDate: string = '';
  loading: boolean = false;
  errorMessage: string = '';

  constructor(
    private apiService: ApiService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.currentWeek();
  }

  loadWeek(): void {
    this.loading = true;
    this.errorMessage = '';
    
    this.apiService.getWeekOverview(this.startDate).subscribe({
      next: (response) => {
        this.weekData = response.week_data || [];
        this.startDate = response.start_date;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading week overview:', error);
        this.errorMessage = 'Fehler beim Laden der Wochenübersicht';
        this.loading = false;
      }
    });
  }

  currentWeek(): void {
    const today = new Date();
    const monday = new Date(today);
    const dayOfWeek = today.getDay();
    const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
    monday.setDate(today.getDate() + diff);
    
    this.startDate = this.formatDateForAPI(monday);
    this.loadWeek();
  }

  previousWeek(): void {
    const date = new Date(this.startDate);
    date.setDate(date.getDate() - 7);
    this.startDate = this.formatDateForAPI(date);
    this.loadWeek();
  }

  nextWeek(): void {
    const date = new Date(this.startDate);
    date.setDate(date.getDate() + 7);
    this.startDate = this.formatDateForAPI(date);
    this.loadWeek();
  }

  selectSlot(date: string, slot: any): void {
    if (slot.is_blocked) return;
    
    if (slot.is_available) {
      this.router.navigate(['/book', date, slot.period]);
    }
  }

  getSlotClass(slot: any): string {
    if (slot.is_blocked) return 'slot-blocked';
    if (slot.is_available) return 'slot-available';
    return 'slot-full';
  }

  getProgressPercent(slot: any): number {
    if (slot.max_students === 0) return 0;
    return (slot.current_students / slot.max_students) * 100;
  }

  getProgressClass(slot: any): string {
    const percent = this.getProgressPercent(slot);
    if (percent < 50) return 'bg-success';
    if (percent < 90) return 'bg-warning';
    return 'bg-danger';
  }

  getWeekdayName(weekday: string): string {
    const days: { [key: string]: string } = {
      'Monday': 'Montag',
      'Tuesday': 'Dienstag',
      'Wednesday': 'Mittwoch',
      'Thursday': 'Donnerstag',
      'Friday': 'Freitag',
      'Saturday': 'Samstag',
      'Sunday': 'Sonntag'
    };
    return days[weekday] || weekday;
  }

  formatDate(dateStr: string): string {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('de-DE', { 
      day: '2-digit', 
      month: '2-digit', 
      year: 'numeric' 
    });
  }

  formatDateShort(dateStr: string): string {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('de-DE', { 
      day: '2-digit', 
      month: '2-digit'
    });
  }

  formatDateForAPI(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
}
