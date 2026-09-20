import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TeachersComponent } from './features/teachers/teachers.component';
import { AbsencesComponent } from './features/absences/absences.component';
import { GuardsComponent } from './features/guards/guards.component';
import { DutyCalendarComponent } from './features/duty-calendar/duty-calendar.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, TeachersComponent, AbsencesComponent, GuardsComponent, DutyCalendarComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  activeTab: 'teachers' | 'absences' | 'guards' | 'duty-calendar' = 'teachers';
}
