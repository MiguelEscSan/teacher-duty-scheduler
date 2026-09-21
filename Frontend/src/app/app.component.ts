import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TeachersComponent } from './features/teachers/teachers.component';
import { AbsencesComponent } from './features/absences/absences.component';
import { GuardsComponent } from './features/guards/guards.component';
import { DutyCalendarComponent } from './features/duty-calendar/duty-calendar.component';
import { ShortTermCalendarComponent } from './features/short-term-calendar/short-term-calendar.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, TeachersComponent, AbsencesComponent, GuardsComponent, DutyCalendarComponent, ShortTermCalendarComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  activeTab: 'teachers' | 'absences' | 'guards' | 'calendars' = 'teachers';
  activeCalendarTab: 'duty' | 'short-term' = 'duty';
}
