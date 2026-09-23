import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AvailableTeacher, ManualAssignmentPayload } from '../models/schedule.model';
import { PeriodResolveResponse, SubstitutionHistory } from '../models/substitutions.model';
import { API_URL } from './api-url';

@Injectable({ providedIn: 'root' })
export class SubstitutionsService {
  private readonly http = inject(HttpClient);

  resolvePeriod(payload: {
    date: string;
    period: number;
    absent_teacher_id: string;
    group_id?: string;
    action: string;
    merged_with_group_id?: string;
  }): Observable<PeriodResolveResponse> {
    return this.http.post<PeriodResolveResponse>(`${API_URL}/substitutions/resolve`, payload);
  }

  sendSubstitutionEmail(payload: {
    date: string;
    period: number;
    absent_teacher_id: string;
    substitute_teacher_id: string;
    group_id?: string;
  }): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${API_URL}/substitutions/send-email`, payload);
  }

  getAvailableCandidates(date: string, period: number): Observable<AvailableTeacher[]> {
    const params = new HttpParams().set('date_str', date).set('period', period.toString());
    return this.http.get<AvailableTeacher[]>(`${API_URL}/substitutions/available-candidates`, { params });
  }

  getSubstitutionHistory(filters?: {
    date?: string;
    substitute_teacher_id?: string;
    absent_teacher_id?: string;
  }): Observable<SubstitutionHistory[]> {
    let params = new HttpParams();
    if (filters?.date) params = params.set('date', filters.date);
    if (filters?.substitute_teacher_id) {
      params = params.set('substitute_teacher_id', filters.substitute_teacher_id);
    }
    if (filters?.absent_teacher_id) params = params.set('absent_teacher_id', filters.absent_teacher_id);
    return this.http.get<SubstitutionHistory[]>(`${API_URL}/substitutions/history`, { params });
  }

  assignManualSubstitution(payload: ManualAssignmentPayload): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${API_URL}/substitutions/assign-manual`, payload);
  }

  markAbsenceAsDoNotCover(payload: {
    date: string;
    period: number;
    absent_teacher_id: string;
  }): Observable<{ message: string; resolved: boolean }> {
    return this.http.post<{ message: string; resolved: boolean }>(
      `${API_URL}/substitutions/do-not-cover`,
      payload
    );
  }
}
