import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-slots',
  template: `
    <div class="card">
      <h2>Verfügbare Slots</h2>
      
      <div class="mb-3">
        <label for="dateSelect" class="form-label">Datum wählen:</label>
        <input 
          type="date" 
          class="form-control" 
          id="dateSelect" 
          [(ngModel)]="selectedDate"
          (change)="loadSlots()">
      </div>
      
      <div *ngIf="loading" class="loading-container">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Laden...</span>
        </div>
      </div>
      
      <div *ngIf="!loading && slots.length > 0">
        <div *ngFor="let slot of slots" 
             class="card mb-2" 
             [ngClass]="getSlotClass(slot)">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h5>{{ slot.period }}. Stunde: {{ slot.label }}</h5>
                <p class="mb-1">{{ slot.start_time }} - {{ slot.end_time }}</p>
                <p class="mb-0">
                  <span *ngIf="!slot.is_blocked">
                    <strong>{{ slot.current_students }}</strong> / {{ slot.max_students }} Schüler
                    ({{ slot.available_spots }} Plätze frei)
                  </span>
                  <span *ngIf="slot.is_blocked" class="text-danger">
                    <strong>Blockiert:</strong> {{ slot.blocked_reason }}
                  </span>
                </p>
              </div>
              <div>
                <button 
                  *ngIf="slot.is_available && !slot.is_blocked" 
                  class="btn btn-primary"
                  (click)="bookSlot(slot)">
                  Buchen
                </button>
                <span *ngIf="slot.is_blocked" class="badge bg-danger">Blockiert</span>
                <span *ngIf="!slot.is_available && !slot.is_blocked" class="badge bg-warning">Voll</span>
              </div>
            </div>
            
            <div *ngIf="slot.bookings && slot.bookings.length > 0" class="mt-2">
              <small class="text-muted">Aktuelle Buchungen:</small>
              <ul class="list-unstyled mb-0">
                <li *ngFor="let booking of slot.bookings">
                  <small>{{ booking.offer_label }} - {{ booking.teacher_name }} ({{ booking.student_count }} Schüler)</small>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      
      <div *ngIf="!loading && slots.length === 0" class="alert alert-info">
        Keine Slots für dieses Datum verfügbar.
      </div>
    </div>
  `,
  styles: []
})
export class SlotsComponent implements OnInit {
  selectedDate: string = '';
  slots: any[] = [];
  loading: boolean = false;

  constructor(
    private apiService: ApiService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.selectedDate = new Date().toISOString().split('T')[0];
    this.loadSlots();
  }

  loadSlots(): void {
    if (!this.selectedDate) return;
    
    this.loading = true;
    this.apiService.getSlots(this.selectedDate).subscribe({
      next: (response) => {
        this.slots = response.slots || [];
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading slots:', error);
        this.loading = false;
      }
    });
  }

  bookSlot(slot: any): void {
    this.router.navigate(['/book', this.selectedDate, slot.period]);
  }

  getSlotClass(slot: any): string {
    if (slot.is_blocked) return 'slot-blocked';
    if (slot.is_available) return 'slot-available';
    return 'slot-full';
  }
}
