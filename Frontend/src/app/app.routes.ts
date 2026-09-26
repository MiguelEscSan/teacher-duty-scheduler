import { Routes } from '@angular/router';
import { TeachersComponent } from './features/teachers/teachers.component';
import { AbsencesComponent } from './features/absences/absences.component';
import { GuardsComponent } from './features/guards/guards.component';
import { SubstitutionHistoryComponent } from './features/substitution-history/substitution-history.component';
import { CalendarLayoutComponent } from './features/calendar-layout/calendar-layout.component';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'teachers' },
  { path: 'teachers', component: TeachersComponent },
  { path: 'absences', component: AbsencesComponent },
  { path: 'guards', component: GuardsComponent },
  { path: 'history', component: SubstitutionHistoryComponent },
  { path: 'substitutions/history', component: SubstitutionHistoryComponent },
  {
    path: 'calendars',
    component: CalendarLayoutComponent,
  },
  { path: '**', redirectTo: 'teachers' }
];
