import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-dashboard',
  template: `
    <div class="card">
      <h2>Willkommen bei SportOase</h2>
      <p class="lead">Das Buchungssystem für Sportstunden</p>
      
      <div class="row mt-4">
        <div class="col-md-4">
          <div class="card bg-primary text-white">
            <div class="card-body">
              <h5 class="card-title">Slots anzeigen</h5>
              <p class="card-text">Sehen Sie verfügbare Zeitslots</p>
              <a routerLink="/slots" class="btn btn-light">Zu den Slots</a>
            </div>
          </div>
        </div>
        
        <div class="col-md-4">
          <div class="card bg-success text-white">
            <div class="card-body">
              <h5 class="card-title">Meine Buchungen</h5>
              <p class="card-text">Verwalten Sie Ihre Buchungen</p>
              <a routerLink="/my-bookings" class="btn btn-light">Meine Buchungen</a>
            </div>
          </div>
        </div>
        
        <div class="col-md-4">
          <div class="card bg-warning text-dark">
            <div class="card-body">
              <h5 class="card-title">Admin-Bereich</h5>
              <p class="card-text">Slots blockieren & verwalten</p>
              <a routerLink="/admin" class="btn btn-dark">Admin-Panel</a>
            </div>
          </div>
        </div>
      </div>
      
      <div class="mt-4">
        <h4>Nächste Schritte:</h4>
        <ol>
          <li>Wählen Sie ein Datum und sehen Sie verfügbare Slots</li>
          <li>Buchen Sie einen Slot für Ihre Klasse</li>
          <li>Verwalten Sie Ihre Buchungen</li>
        </ol>
      </div>
    </div>
  `,
  styles: [`
    .card { margin-bottom: 1rem; }
    .row { margin-top: 2rem; }
  `]
})
export class DashboardComponent implements OnInit {
  constructor(private apiService: ApiService) { }

  ngOnInit(): void {
  }
}
