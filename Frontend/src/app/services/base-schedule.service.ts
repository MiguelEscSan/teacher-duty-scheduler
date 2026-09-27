import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject, tap } from 'rxjs';
import { BaseSlot, DutySlot, StudentGroup } from '../models/schedule.model';
import { API_URL } from './api-url';

export type DutyType = 'FIXED_DUTY' | 'SHORT_TERM';

export interface DutyAssignmentPayload {
  teacher_id: string;
  day_of_week: number;
  period: number;
  duty_type: DutyType;
}

export interface DutyAssignmentResponse {
  message: string;
  teacher_id: string;
  day_of_week: number;
  period: number;
  duty_type: DutyType;
}

@Injectable({ providedIn: 'root' })
export class BaseScheduleService {
  private readonly http = inject(HttpClient);
  private readonly groupDeletedSubject = new Subject<string>();
  readonly groupDeleted$ = this.groupDeletedSubject.asObservable();

  getGroups(): Observable<StudentGroup[]> {
    return this.http.get<StudentGroup[]>(`${API_URL}/groups`);
  }

  createGroup(payload: { name: string; student_count: number | null }): Observable<StudentGroup> {
    return this.http.post<StudentGroup>(`${API_URL}/groups`, payload);
  }

  updateGroup(id: string, payload: { name: string; student_count: number | null }): Observable<StudentGroup> {
    return this.http.put<StudentGroup>(`${API_URL}/groups/${id}`, payload);
  }

  deleteGroup(groupId: string): Observable<void> {
    return this.http.delete<void>(`${API_URL}/groups/${groupId}`).pipe(
      tap(() => this.groupDeletedSubject.next(groupId))
    );
  }

  assignSlotGroup(teacherId: string, day: number, period: number, groupId: string | null): Observable<any> {
    return this.http.put(`${API_URL}/base-schedule/assign-slot`, {
      teacher_id: teacherId,
      day,
      period,
      group_id: groupId
    });
  }

  updateSlotStatus(
    teacherId: string,
    day: number,
    period: number,
    status: 'FREE' | 'NON_PRESENTIAL' | 'TEACHING',
    groupId: string | null = null
  ): Observable<{ status: string }> {
    return this.http.put<{ status: string }>(`${API_URL}/base-schedule/slot-status`, {
      teacher_id: teacherId,
      day,
      period,
      status,
      group_id: groupId
    });
  }

  getBaseSchedule(teacherId: string): Observable<BaseSlot[][]> {
    return this.http.get<BaseSlot[][]>(`${API_URL}/base-schedule/${teacherId}`);
  }

  getDutyTeachers(filters?: { day_of_week?: number; period?: number }): Observable<DutySlot[]> {
    return this.http.get<DutySlot[]>(`${API_URL}/base-schedule/duty`, {
      params: this.toDutyParams(filters)
    });
  }

  getShortTermTeachers(filters?: { day_of_week?: number; period?: number }): Observable<DutySlot[]> {
    return this.http.get<DutySlot[]>(`${API_URL}/base-schedule/short-term`, {
      params: this.toDutyParams(filters)
    });
  }

  assignDuty(payload: DutyAssignmentPayload): Observable<DutyAssignmentResponse> {
    return this.http.post<DutyAssignmentResponse>(`${API_URL}/base-schedule/duty-assignment`, payload);
  }

  removeDuty(payload: DutyAssignmentPayload): Observable<DutyAssignmentResponse> {
    return this.http.delete<DutyAssignmentResponse>(`${API_URL}/base-schedule/duty-assignment`, { body: payload });
  }

  private toDutyParams(filters?: { day_of_week?: number; period?: number }): Record<string, string> {
    const params: Record<string, string> = {};
    if (filters?.day_of_week !== undefined) params['day_of_week'] = filters.day_of_week.toString();
    if (filters?.period !== undefined) params['period'] = filters.period.toString();
    return params;
  }
}
