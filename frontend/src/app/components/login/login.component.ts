import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-login',
  template: `
    <div class="card login-card">
      <h2>SportOase Login</h2>
      <p class="text-muted">Entwicklungsumgebung - Testanmeldung</p>
      
      <form (ngSubmit)="login()">
        <div class="mb-3">
          <label class="form-label">Benutzername</label>
          <input 
            type="text" 
            class="form-control" 
            [(ngModel)]="username"
            name="username"
            placeholder="testuser">
        </div>
        
        <div class="mb-3">
          <label class="form-label">Passwort</label>
          <input 
            type="password" 
            class="form-control" 
            [(ngModel)]="password"
            name="password"
            placeholder="test123">
        </div>
        
        <div *ngIf="errorMessage" class="alert alert-danger">
          {{ errorMessage }}
        </div>
        
        <button type="submit" class="btn btn-primary w-100" [disabled]="loading">
          <span *ngIf="!loading">Anmelden</span>
          <span *ngIf="loading">
            <span class="spinner-border spinner-border-sm me-2"></span>
            Anmelden...
          </span>
        </button>
      </form>
      
      <div class="mt-3 alert alert-info">
        <strong>Test-Zugangsdaten:</strong><br>
        Benutzername: testuser<br>
        Passwort: test123
      </div>
    </div>
  `,
  styles: [`
    .login-card {
      max-width: 400px;
      margin: 50px auto;
      padding: 30px;
    }
  `]
})
export class LoginComponent {
  username: string = '';
  password: string = '';
  loading: boolean = false;
  errorMessage: string = '';

  constructor(
    private http: HttpClient,
    private router: Router
  ) { }

  login(): void {
    this.loading = true;
    this.errorMessage = '';
    
    this.http.post('/api/sportoase/login', {
      username: this.username,
      password: this.password
    }, { withCredentials: true }).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/dashboard']);
      },
      error: (error) => {
        this.loading = false;
        this.errorMessage = error.error?.error || 'Login fehlgeschlagen';
      }
    });
  }
}
