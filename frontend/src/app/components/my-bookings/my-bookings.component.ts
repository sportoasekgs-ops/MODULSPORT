import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-my-bookings',
  template: `
    <div class="card">
      <h2>Meine Buchungen</h2>
      
      <div *ngIf="loading" class="loading-container">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Laden...</span>
        </div>
      </div>
      
      <div *ngIf="!loading && bookings.length > 0">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Datum</th>
              <th>Stunde</th>
              <th>Angebot</th>
              <th>Schüler</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let booking of bookings">
              <td>{{ booking.date }}</td>
              <td>{{ booking.period }}. Stunde</td>
              <td>{{ booking.offer_label }}</td>
              <td>{{ booking.student_count }} Schüler</td>
              <td>
                <button class="btn btn-sm btn-danger" (click)="deleteBooking(booking.id)">
                  Löschen
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div *ngIf="!loading && bookings.length === 0" class="alert alert-info">
        Sie haben noch keine Buchungen.
      </div>
      
      <div *ngIf="successMessage" class="alert alert-success mt-3">
        {{ successMessage }}
      </div>
      
      <div *ngIf="errorMessage" class="alert alert-danger mt-3">
        {{ errorMessage }}
      </div>
    </div>
  `,
  styles: []
})
export class MyBookingsComponent implements OnInit {
  bookings: any[] = [];
  loading: boolean = false;
  successMessage: string = '';
  errorMessage: string = '';

  constructor(private apiService: ApiService) { }

  ngOnInit(): void {
    this.loadBookings();
  }

  loadBookings(): void {
    this.loading = true;
    this.apiService.getMyBookings().subscribe({
      next: (response) => {
        this.bookings = response.bookings || [];
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading bookings:', error);
        this.loading = false;
        this.errorMessage = 'Fehler beim Laden der Buchungen';
      }
    });
  }

  deleteBooking(bookingId: number): void {
    if (!confirm('Möchten Sie diese Buchung wirklich löschen?')) {
      return;
    }
    
    this.apiService.deleteBooking(bookingId).subscribe({
      next: (response) => {
        this.successMessage = 'Buchung erfolgreich gelöscht';
        this.loadBookings();
        setTimeout(() => this.successMessage = '', 3000);
      },
      error: (error) => {
        this.errorMessage = error.error?.error || 'Fehler beim Löschen der Buchung';
        setTimeout(() => this.errorMessage = '', 3000);
      }
    });
  }
}
