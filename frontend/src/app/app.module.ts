import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule, Routes } from '@angular/router';

import { AppComponent } from './app.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { SlotsComponent } from './components/slots/slots.component';
import { BookingFormComponent } from './components/booking-form/booking-form.component';
import { MyBookingsComponent } from './components/my-bookings/my-bookings.component';
import { AdminPanelComponent } from './components/admin-panel/admin-panel.component';
import { WeekOverviewComponent } from './components/week-overview/week-overview.component';

import { ApiService } from './services/api.service';

const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'week-overview', component: WeekOverviewComponent },
  { path: 'slots', component: SlotsComponent },
  { path: 'book/:date/:period', component: BookingFormComponent },
  { path: 'my-bookings', component: MyBookingsComponent },
  { path: 'admin', component: AdminPanelComponent },
];

@NgModule({
  declarations: [
    AppComponent,
    DashboardComponent,
    WeekOverviewComponent,
    SlotsComponent,
    BookingFormComponent,
    MyBookingsComponent,
    AdminPanelComponent,
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    RouterModule.forRoot(routes),
  ],
  providers: [ApiService],
  bootstrap: [AppComponent]
})
export class AppModule { }
