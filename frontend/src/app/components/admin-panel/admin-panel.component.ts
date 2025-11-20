import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-admin-panel',
  template: `
    <div class="card">
      <h2>Admin-Panel</h2>
      <p class="text-muted">Kurse verwalten, Slots blockieren und Benachrichtigungen verwalten</p>
      
      <h4 class="mt-4">Kursnamen verwalten</h4>
      <div *ngIf="loadingTimeslots" class="text-center">
        <div class="spinner-border" role="status"></div>
      </div>
      
      <div *ngIf="!loadingTimeslots && timeslots.length > 0">
        <table class="table table-bordered">
          <thead>
            <tr>
              <th>Wochentag</th>
              <th>Stunde</th>
              <th>Kursname</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let slot of timeslots">
              <td>{{ getWeekdayName(slot.weekday) }}</td>
              <td>{{ slot.period }}. Stunde ({{ slot.start_time }} - {{ slot.end_time }})</td>
              <td>
                <span *ngIf="!slot.editing">{{ slot.label }}</span>
                <input *ngIf="slot.editing" 
                       type="text" 
                       class="form-control" 
                       [(ngModel)]="slot.newLabel" 
                       (keyup.enter)="saveTimeslotLabel(slot)"
                       (keyup.escape)="cancelEdit(slot)">
              </td>
              <td>
                <button *ngIf="!slot.editing" 
                        class="btn btn-sm btn-primary me-2" 
                        (click)="editTimeslot(slot)">
                  Bearbeiten
                </button>
                <button *ngIf="slot.editing" 
                        class="btn btn-sm btn-success me-2" 
                        (click)="saveTimeslotLabel(slot)">
                  Speichern
                </button>
                <button *ngIf="slot.editing" 
                        class="btn btn-sm btn-secondary" 
                        (click)="cancelEdit(slot)">
                  Abbrechen
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <h4 class="mt-4">Slot blockieren</h4>
      <form [formGroup]="blockForm" (ngSubmit)="blockSlot()">
        <div class="row">
          <div class="col-md-4">
            <label class="form-label">Datum</label>
            <input type="date" class="form-control" formControlName="date">
          </div>
          <div class="col-md-2">
            <label class="form-label">Stunde</label>
            <input type="number" class="form-control" formControlName="period" min="1" max="6">
          </div>
          <div class="col-md-4">
            <label class="form-label">Grund</label>
            <input type="text" class="form-control" formControlName="reason" placeholder="Beratung">
          </div>
          <div class="col-md-2">
            <label class="form-label">&nbsp;</label>
            <button type="submit" class="btn btn-warning w-100" [disabled]="!blockForm.valid">
              Blockieren
            </button>
          </div>
        </div>
      </form>
      
      <div *ngIf="successMessage" class="alert alert-success mt-3">
        {{ successMessage }}
      </div>
      
      <div *ngIf="errorMessage" class="alert alert-danger mt-3">
        {{ errorMessage }}
      </div>
      
      <h4 class="mt-4">Blockierte Slots</h4>
      <div *ngIf="loadingBlocked" class="text-center">
        <div class="spinner-border" role="status"></div>
      </div>
      
      <div *ngIf="!loadingBlocked && blockedSlots.length > 0">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Datum</th>
              <th>Stunde</th>
              <th>Grund</th>
              <th>Blockiert von</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let slot of blockedSlots">
              <td>{{ slot.date }}</td>
              <td>{{ slot.period }}. Stunde</td>
              <td>{{ slot.reason }}</td>
              <td>{{ slot.blocked_by }}</td>
              <td>
                <button class="btn btn-sm btn-success" (click)="unblockSlot(slot)">
                  Freigeben
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div *ngIf="!loadingBlocked && blockedSlots.length === 0" class="alert alert-info">
        Keine blockierten Slots vorhanden.
      </div>
    </div>
  `,
  styles: []
})
export class AdminPanelComponent implements OnInit {
  blockForm: FormGroup;
  blockedSlots: any[] = [];
  timeslots: any[] = [];
  loadingBlocked: boolean = false;
  loadingTimeslots: boolean = false;
  successMessage: string = '';
  errorMessage: string = '';

  constructor(
    private fb: FormBuilder,
    private apiService: ApiService
  ) {
    this.blockForm = this.fb.group({
      date: ['', Validators.required],
      period: ['', [Validators.required, Validators.min(1), Validators.max(6)]],
      reason: ['Beratung']
    });
  }

  ngOnInit(): void {
    this.loadBlockedSlots();
    this.loadTimeslots();
  }

  loadTimeslots(): void {
    this.loadingTimeslots = true;
    this.apiService.getTimeslots().subscribe({
      next: (response) => {
        this.timeslots = response.timeslots.map((ts: any) => ({
          ...ts,
          editing: false,
          newLabel: ts.label
        }));
        this.loadingTimeslots = false;
      },
      error: (error) => {
        console.error('Error loading timeslots:', error);
        this.loadingTimeslots = false;
      }
    });
  }

  editTimeslot(slot: any): void {
    this.timeslots.forEach(s => s.editing = false);
    slot.editing = true;
    slot.newLabel = slot.label;
  }

  cancelEdit(slot: any): void {
    slot.editing = false;
    slot.newLabel = slot.label;
  }

  saveTimeslotLabel(slot: any): void {
    if (!slot.newLabel || slot.newLabel.trim() === '') {
      this.errorMessage = 'Kursname darf nicht leer sein';
      setTimeout(() => this.errorMessage = '', 3000);
      return;
    }

    this.apiService.updateTimeslotLabel(slot.id, slot.newLabel).subscribe({
      next: (response) => {
        slot.label = slot.newLabel;
        slot.editing = false;
        this.successMessage = 'Kursname erfolgreich aktualisiert';
        setTimeout(() => this.successMessage = '', 3000);
      },
      error: (error) => {
        this.errorMessage = error.error?.error || 'Fehler beim Aktualisieren des Kursnamens';
        setTimeout(() => this.errorMessage = '', 3000);
      }
    });
  }

  getWeekdayName(weekday: string): string {
    const days: { [key: string]: string } = {
      'Mon': 'Montag',
      'Tue': 'Dienstag',
      'Wed': 'Mittwoch',
      'Thu': 'Donnerstag',
      'Fri': 'Freitag',
      'Sat': 'Samstag',
      'Sun': 'Sonntag'
    };
    return days[weekday] || weekday;
  }

  loadBlockedSlots(): void {
    this.loadingBlocked = true;
    this.apiService.getBlockedSlots().subscribe({
      next: (response) => {
        this.blockedSlots = response.blocked_slots || [];
        this.loadingBlocked = false;
      },
      error: (error) => {
        console.error('Error loading blocked slots:', error);
        this.loadingBlocked = false;
      }
    });
  }

  blockSlot(): void {
    if (!this.blockForm.valid) return;
    
    const formValue = this.blockForm.value;
    const slotData = {
      date: formValue.date,
      weekday: this.getWeekday(formValue.date),
      period: parseInt(formValue.period),
      reason: formValue.reason || 'Beratung'
    };
    
    this.apiService.blockSlot(slotData).subscribe({
      next: (response) => {
        this.successMessage = 'Slot erfolgreich blockiert';
        this.blockForm.reset({ reason: 'Beratung' });
        this.loadBlockedSlots();
        setTimeout(() => this.successMessage = '', 3000);
      },
      error: (error) => {
        this.errorMessage = error.error?.error || 'Fehler beim Blockieren des Slots';
        setTimeout(() => this.errorMessage = '', 3000);
      }
    });
  }

  unblockSlot(slot: any): void {
    if (!confirm(`Möchten Sie den Slot am ${slot.date} (${slot.period}. Stunde) wirklich freigeben?`)) {
      return;
    }
    
    const slotData = {
      date: slot.date,
      period: slot.period
    };
    
    this.apiService.unblockSlot(slotData).subscribe({
      next: (response) => {
        this.successMessage = 'Slot erfolgreich freigegeben';
        this.loadBlockedSlots();
        setTimeout(() => this.successMessage = '', 3000);
      },
      error: (error) => {
        this.errorMessage = error.error?.error || 'Fehler beim Freigeben des Slots';
        setTimeout(() => this.errorMessage = '', 3000);
      }
    });
  }

  private getWeekday(dateStr: string): string {
    const date = new Date(dateStr);
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    return days[date.getDay()];
  }
}
