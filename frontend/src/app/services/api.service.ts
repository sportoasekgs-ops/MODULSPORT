import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = '/api/sportoase';
  private csrfToken: string = '';

  constructor(private http: HttpClient) {
    this.initCsrfToken();
  }

  private initCsrfToken(): void {
    this.http.get<any>(`${this.apiUrl}/csrf`, { withCredentials: true }).subscribe(
      response => {
        this.csrfToken = response.csrfToken;
      },
      error => console.error('Failed to get CSRF token:', error)
    );
  }

  private getHeaders(): HttpHeaders {
    let headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });
    
    if (this.csrfToken) {
      headers = headers.set('X-CSRFToken', this.csrfToken);
    }
    
    return headers;
  }

  getSlots(date: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/slots?date=${date}`, { withCredentials: true });
  }

  getWeekOverview(startDate?: string): Observable<any> {
    let url = `${this.apiUrl}/slots/week`;
    if (startDate) {
      url += `?start_date=${startDate}`;
    }
    return this.http.get(url, { withCredentials: true });
  }

  getTimeslots(): Observable<any> {
    return this.http.get(`${this.apiUrl}/timeslots`, { withCredentials: true });
  }

  createBooking(bookingData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/book`, bookingData, { 
      headers: this.getHeaders(),
      withCredentials: true
    });
  }

  getMyBookings(startDate?: string, endDate?: string): Observable<any> {
    let url = `${this.apiUrl}/my-bookings`;
    const params: string[] = [];
    
    if (startDate) params.push(`start_date=${startDate}`);
    if (endDate) params.push(`end_date=${endDate}`);
    
    if (params.length > 0) {
      url += '?' + params.join('&');
    }
    
    return this.http.get(url, { withCredentials: true });
  }

  deleteBooking(bookingId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/bookings/${bookingId}`, {
      headers: this.getHeaders(),
      withCredentials: true
    });
  }

  blockSlot(slotData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/block-slot`, slotData, { 
      headers: this.getHeaders(),
      withCredentials: true
    });
  }

  unblockSlot(slotData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/unblock-slot`, slotData, { 
      headers: this.getHeaders(),
      withCredentials: true
    });
  }

  getBlockedSlots(): Observable<any> {
    return this.http.get(`${this.apiUrl}/blocked-slots`, { withCredentials: true });
  }

  getAllBookings(date?: string): Observable<any> {
    let url = `${this.apiUrl}/bookings`;
    if (date) {
      url += `?date=${date}`;
    }
    return this.http.get(url, { withCredentials: true });
  }

  getNotifications(unreadOnly: boolean = false): Observable<any> {
    let url = `${this.apiUrl}/notifications`;
    if (unreadOnly) {
      url += '?unread_only=true';
    }
    return this.http.get(url, { withCredentials: true });
  }

  markNotificationRead(notificationId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/notifications/${notificationId}/mark-read`, {}, { 
      headers: this.getHeaders(),
      withCredentials: true
    });
  }
}
