import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Absence } from '../models/schedule.model';
import { AbsencePreviewResponse } from '../models/substitutions.model';
import { API_URL } from './api-url';

@Injectable({ providedIn: 'root' })
export class AbsencesService {
  private readonly http = inject(HttpClient);

  getAbsences(filters?: {
    date?: string;
    teacher_id?: string;
    resolved?: boolean;
  }): Observable<Absence[]> {
    let params = new HttpParams();
    if (filters?.date) params = params.set('date', filters.date);
    if (filters?.teacher_id) params = params.set('teacher_id', filters.teacher_id);
    if (filters?.resolved !== undefined) params = params.set('resolved', filters.resolved.toString());
    return this.http.get<Absence[]>(`${API_URL}/absences`, { params });
  }

  addAbsence(absence: Absence): Observable<Absence> {
    return this.http.post<Absence>(`${API_URL}/absences`, absence);
  }

  deleteAbsence(absenceId: number): Observable<any> {
    return this.http.delete(`${API_URL}/absences/${absenceId}`);
  }

  previewDayAbsence(teacherId: string, date: string): Observable<AbsencePreviewResponse> {
    return this.http.post<AbsencePreviewResponse>(`${API_URL}/absences/preview-day`, {
      teacher_id: teacherId,
      date
    });
  }
}
