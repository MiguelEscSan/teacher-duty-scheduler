import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DutyCalendarComponent } from '../duty-calendar/duty-calendar.component';
import { ShortTermCalendarComponent } from '../short-term-calendar/short-term-calendar.component';

@Component({
  selector: 'app-calendar-layout',
  standalone: true,
  imports: [CommonModule, DutyCalendarComponent, ShortTermCalendarComponent],
  templateUrl: './calendar-layout.component.html',
  styleUrls: ['./calendar-layout.component.css']
})
export class CalendarLayoutComponent {
  activeTab: 'duty' | 'short-term' = 'duty';
}
