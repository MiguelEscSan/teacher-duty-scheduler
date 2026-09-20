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
import {AbsencePreviewResponse, PeriodResolveResponse} from '../models/substitutions.model';
import {ManualAssignmentPayload} from '../models/schedule.model';

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

  getGroups(): Observable<StudentGroup[]> {
    return this.http.get<StudentGroup[]>(`${this.url}/groups`);
  }

  assignSlotGroup(teacherId: string, day: number, period: number, groupId: string | null): Observable<any> {
    return this.http.put(`${this.url}/base-schedule/assign-slot`, {
      teacher_id: teacherId,
      day,
      period,
      group_id: groupId
    });
  }

  // --- Despacho Operativo v1 ---
  previewDayAbsence(teacherId: string, date: string): Observable<AbsencePreviewResponse> {
    return this.http.post<AbsencePreviewResponse>(`${this.url}/v1/absences/preview-day`, {
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
    return this.http.post<PeriodResolveResponse>(`${this.url}/v1/substitutions/resolve`, payload);
  }

  sendSubstitutionEmail(payload: {
    date: string;
    period: number;
    absent_teacher_id: string;
    substitute_teacher_id: string;
    group_id?: string;
  }): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(
      `${this.url}/v1/substitutions/send-email`,
      payload
    );
  }

  getAvailableCandidates(date: string, period: number): Observable<AvailableTeacher[]> {
    const params = new HttpParams()
      .set('date_str', date)
      .set('period', period.toString());
    return this.http.get<AvailableTeacher[]>(`${this.url}/v1/substitutions/available-candidates`, { params });
  }

  getDutyTeachers(): Observable<DutySlot[]> {
    return this.http.get<DutySlot[]>(`${this.url}/v1/substitutions/duty-teachers`);
  }

  getShortTermTeachers(): Observable<DutySlot[]> {
    return this.http.get<DutySlot[]>(`${this.url}/v1/substitutions/short-term-teachers`);
  }

  // 2. Asignar sustitución manual
  assignManualSubstitution(payload: ManualAssignmentPayload): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.url}/assign-manual`, payload);
  }

  markAbsenceAsDoNotCover(payload: {
    date: string;
    period: number;
    absent_teacher_id: string;
  }): Observable<{ message: string; resolved: boolean }> {
    return this.http.post<{ message: string; resolved: boolean }>(
      `${this.url}/v1/substitutions/do-not-cover`,
      payload
    );
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
