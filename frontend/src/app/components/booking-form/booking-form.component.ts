import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators, FormArray } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-booking-form',
  template: `
    <div class="card">
      <h2>Slot buchen</h2>
      <p>Datum: {{ date }} - {{ period }}. Stunde</p>
      
      <form [formGroup]="bookingForm" (ngSubmit)="submitBooking()">
        <div class="mb-3">
          <label class="form-label">Angebotsart</label>
          <select class="form-select" formControlName="offer_type">
            <option value="sport">Sport</option>
            <option value="games">Spiele</option>
            <option value="outdoor">Outdoor</option>
            <option value="other">Sonstiges</option>
          </select>
        </div>
        
        <div class="mb-3">
          <label class="form-label">Angebotsbezeichnung</label>
          <input type="text" class="form-control" formControlName="offer_label" 
                 placeholder="z.B. Basketball, Fußball, etc.">
        </div>
        
        <div class="mb-3">
          <label class="form-label">Lehrkraft Name</label>
          <input type="text" class="form-control" formControlName="teacher_name">
        </div>
        
        <div class="mb-3">
          <label class="form-label">Klasse</label>
          <input type="text" class="form-control" formControlName="teacher_class"
                 placeholder="z.B. 5a, 6b, etc.">
        </div>
        
        <div class="mb-3">
          <label class="form-label">Schüler</label>
          <div formArrayName="students">
            <div *ngFor="let student of students.controls; let i = index" [formGroupName]="i" class="mb-2">
              <div class="row">
                <div class="col-md-5">
                  <input type="text" class="form-control" formControlName="name" placeholder="Name">
                </div>
                <div class="col-md-5">
                  <input type="text" class="form-control" formControlName="klasse" placeholder="Klasse">
                </div>
                <div class="col-md-2">
                  <button type="button" class="btn btn-danger" (click)="removeStudent(i)">
                    Entfernen
                  </button>
                </div>
              </div>
            </div>
          </div>
          <button type="button" class="btn btn-secondary mt-2" (click)="addStudent()">
            + Schüler hinzufügen
          </button>
        </div>
        
        <div class="d-flex gap-2">
          <button type="submit" class="btn btn-primary" [disabled]="!bookingForm.valid || submitting">
            {{ submitting ? 'Wird gespeichert...' : 'Buchen' }}
          </button>
          <button type="button" class="btn btn-secondary" (click)="cancel()">
            Abbrechen
          </button>
        </div>
        
        <div *ngIf="errorMessage" class="alert alert-danger mt-3">
          {{ errorMessage }}
        </div>
        
        <div *ngIf="successMessage" class="alert alert-success mt-3">
          {{ successMessage }}
        </div>
      </form>
    </div>
  `,
  styles: []
})
export class BookingFormComponent implements OnInit {
  date: string = '';
  period: number = 0;
  weekday: string = '';
  bookingForm: FormGroup;
  submitting: boolean = false;
  errorMessage: string = '';
  successMessage: string = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private fb: FormBuilder,
    private apiService: ApiService
  ) {
    this.bookingForm = this.fb.group({
      offer_type: ['sport', Validators.required],
      offer_label: ['', Validators.required],
      teacher_name: ['', Validators.required],
      teacher_class: [''],
      students: this.fb.array([])
    });
  }

  ngOnInit(): void {
    this.date = this.route.snapshot.paramMap.get('date') || '';
    this.period = parseInt(this.route.snapshot.paramMap.get('period') || '0');
    this.weekday = this.getWeekday(this.date);
    
    this.addStudent();
  }

  get students(): FormArray {
    return this.bookingForm.get('students') as FormArray;
  }

  addStudent(): void {
    this.students.push(this.fb.group({
      name: ['', Validators.required],
      klasse: ['', Validators.required]
    }));
  }

  removeStudent(index: number): void {
    this.students.removeAt(index);
  }

  submitBooking(): void {
    if (!this.bookingForm.valid) return;
    
    this.submitting = true;
    this.errorMessage = '';
    this.successMessage = '';
    
    const bookingData = {
      date: this.date,
      weekday: this.weekday,
      period: this.period,
      ...this.bookingForm.value
    };
    
    this.apiService.createBooking(bookingData).subscribe({
      next: (response) => {
        this.submitting = false;
        this.successMessage = 'Buchung erfolgreich erstellt!';
        setTimeout(() => {
          this.router.navigate(['/my-bookings']);
        }, 2000);
      },
      error: (error) => {
        this.submitting = false;
        this.errorMessage = error.error?.error || 'Fehler beim Erstellen der Buchung';
      }
    });
  }

  cancel(): void {
    this.router.navigate(['/slots']);
  }

  private getWeekday(dateStr: string): string {
    const date = new Date(dateStr);
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    return days[date.getDay()];
  }
}
