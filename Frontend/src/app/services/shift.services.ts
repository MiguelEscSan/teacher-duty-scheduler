import { Injectable, inject } from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Absence,
  AvailableTeacher,
  BaseSlot,
  DutySlot,
  OptimizationResponse,
  StudentGroup,
  Teacher
} from '../models/schedule.model';
import {
  AbsencePreviewResponse,
  PeriodResolveResponse,
  SubstitutionHistory
} from '../models/substitutions.model';
import {ManualAssignmentPayload} from '../models/schedule.model';

@Injectable({ providedIn: 'root' })
export class GuardiasService {
  private http = inject(HttpClient);
  private url = 'http://localhost:8000/api/v1';

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

  getGroups(): Observable<StudentGroup[]> {
    return this.http.get<StudentGroup[]>(`${this.url}/base-schedule/groups`);
  }

  assignSlotGroup(teacherId: string, day: number, period: number, groupId: string | null): Observable<any> {
    return this.http.put(`${this.url}/base-schedule/assign-slot`, {
      teacher_id: teacherId,
      day,
      period,
      group_id: groupId
    });
  }

  previewDayAbsence(teacherId: string, date: string): Observable<AbsencePreviewResponse> {
    return this.http.post<AbsencePreviewResponse>(`${this.url}/absences/preview-day`, {
      teacher_id: teacherId,
      date
    });
  }

  resolvePeriod(payload: {
    date: string;
    period: number;
    absent_teacher_id: string;
    group_id?: string;
    action: string;
    merged_with_group_id?: string;
  }): Observable<PeriodResolveResponse> {
    return this.http.post<PeriodResolveResponse>(`${this.url}/substitutions/resolve`, payload);
  }

  sendSubstitutionEmail(payload: {
    date: string;
    period: number;
    absent_teacher_id: string;
    substitute_teacher_id: string;
    group_id?: string;
  }): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(
      `${this.url}/substitutions/send-email`,
      payload
    );
  }

  getAvailableCandidates(date: string, period: number): Observable<AvailableTeacher[]> {
    const params = new HttpParams()
      .set('date_str', date)
      .set('period', period.toString());
    return this.http.get<AvailableTeacher[]>(`${this.url}/substitutions/available-candidates`, { params });
  }

  getDutyTeachers(): Observable<DutySlot[]> {
    return this.http.get<DutySlot[]>(`${this.url}/teachers/duty`);
  }

  getShortTermTeachers(): Observable<DutySlot[]> {
    return this.http.get<DutySlot[]>(`${this.url}/teachers/short-term`);
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
    if (filters?.absent_teacher_id) {
      params = params.set('absent_teacher_id', filters.absent_teacher_id);
    }

    return this.http.get<SubstitutionHistory[]>(`${this.url}/substitutions/history`, { params });
  }

  // 2. Asignar sustitución manual
  assignManualSubstitution(payload: ManualAssignmentPayload): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.url}/substitutions/assign-manual`, payload);
  }

  markAbsenceAsDoNotCover(payload: {
    date: string;
    period: number;
    absent_teacher_id: string;
  }): Observable<{ message: string; resolved: boolean }> {
    return this.http.post<{ message: string; resolved: boolean }>(
      `${this.url}/substitutions/do-not-cover`,
      payload
    );
  }

  getBaseSchedule(teacherId: string): Observable<BaseSlot[][]> {
    return this.http.get<BaseSlot[][]>(`${this.url}/base-schedule/${teacherId}`);
  }

  toggleSlot(teacherId: string, day: number, period: number): Observable<any> {
    return this.http.put(`${this.url}/base-schedule/toggle`, {
      teacher_id: teacherId,
      day,
      period
    });
  }

  // Ausencias
  getAbsences(filters?: {
    date?: string;
    teacher_id?: string;
    resolved?: boolean;
  }): Observable<Absence[]> {
    let params = new HttpParams();
    if (filters?.date) params = params.set('date', filters.date);
    if (filters?.teacher_id) params = params.set('teacher_id', filters.teacher_id);
    if (filters?.resolved !== undefined) params = params.set('resolved', filters.resolved.toString());

    return this.http.get<Absence[]>(`${this.url}/absences`, { params });
  }

  addAbsence(absence: Absence): Observable<Absence> {
    return this.http.post<Absence>(`${this.url}/absences`, absence);
  }

  deleteAbsence(absenceId: number): Observable<any> {
    return this.http.delete(`${this.url}/absences/${absenceId}`);
  }

  // Optimización por fecha
  optimizeWeek(startDate: string): Observable<OptimizationResponse> {
    return this.http.post<OptimizationResponse>(`${this.url}/guards/optimize`, {
      start_date: startDate
    });
  }
}
