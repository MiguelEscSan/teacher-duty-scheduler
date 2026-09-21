import { Routes } from '@angular/router';
import { TeachersComponent } from './features/teachers/teachers.component';
import { AbsencesComponent } from './features/absences/absences.component';
import { GuardsComponent } from './features/guards/guards.component';
import { DutyCalendarComponent } from './features/duty-calendar/duty-calendar.component';
import { ShortTermCalendarComponent } from './features/short-term-calendar/short-term-calendar.component';
import { SubstitutionHistoryComponent } from './features/substitution-history/substitution-history.component';
import { CalendarLayoutComponent } from './features/calendar-layout/calendar-layout.component';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'teachers' },
  { path: 'teachers', component: TeachersComponent },
  { path: 'absences', component: AbsencesComponent },
  { path: 'guards', component: GuardsComponent },
  { path: 'history', component: SubstitutionHistoryComponent },
  {
    path: 'calendars',
    component: CalendarLayoutComponent,
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'duty' },
      { path: 'duty', component: DutyCalendarComponent },
      { path: 'short-term', component: ShortTermCalendarComponent }
    ]
  },
  { path: '**', redirectTo: 'teachers' }
];
