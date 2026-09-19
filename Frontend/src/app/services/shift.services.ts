import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Absence, BaseSlot, OptimizationResponse, Teacher } from '../models/schedule.model';

@Injectable({ providedIn: 'root' })
export class GuardiasService {
  private http = inject(HttpClient);
  private url = 'http://localhost:8000/api';

  // Profesores
  getTeachers(): Observable<Teacher[]> {
    return this.http.get<Teacher[]>(`${this.url}/teachers`);
  }

  addTeacher(teacher: Teacher): Observable<Teacher> {
    return this.http.post<Teacher>(`${this.url}/teachers`, teacher);
  }

  deleteTeacher(id: string): Observable<any> {
    return this.http.delete(`${this.url}/teachers/${id}`);
  }

  // Horario Base
  getBaseSchedule(teacherId: string): Observable<BaseSlot[][]> {
    return this.http.get<BaseSlot[][]>(`${this.url}/teachers/${teacherId}/base-schedule`);
  }

  toggleSlot(teacherId: string, day: number, period: number): Observable<any> {
    return this.http.put(`${this.url}/base-schedule/toggle`, {
      teacher_id: teacherId,
      day,
      period
    });
  }

  // Ausencias
  getAbsences(): Observable<Absence[]> {
    return this.http.get<Absence[]>(`${this.url}/absences`);
  }

  addAbsence(absence: Absence): Observable<Absence> {
    return this.http.post<Absence>(`${this.url}/absences`, absence);
  }

  deleteAbsence(absenceId: number): Observable<any> {
    return this.http.delete(`${this.url}/absences/${absenceId}`);
  }

  // Optimización por fecha
  optimizeWeek(startDate: string): Observable<OptimizationResponse> {
    return this.http.post<OptimizationResponse>(`${this.url}/optimize`, {
      start_date: startDate
    });
  }
}
