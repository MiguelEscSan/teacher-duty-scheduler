import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { BaseSlot, StudentGroup } from '../models/schedule.model';
import { API_URL } from './api-url';

@Injectable({ providedIn: 'root' })
export class BaseScheduleService {
  private readonly http = inject(HttpClient);

  getGroups(): Observable<StudentGroup[]> {
    return this.http.get<StudentGroup[]>(`${API_URL}/base-schedule/groups`);
  }

  assignSlotGroup(teacherId: string, day: number, period: number, groupId: string | null): Observable<any> {
    return this.http.put(`${API_URL}/base-schedule/assign-slot`, {
      teacher_id: teacherId,
      day,
      period,
      group_id: groupId
    });
  }

  getBaseSchedule(teacherId: string): Observable<BaseSlot[][]> {
    return this.http.get<BaseSlot[][]>(`${API_URL}/base-schedule/${teacherId}`);
  }

  toggleSlot(teacherId: string, day: number, period: number): Observable<any> {
    return this.http.put(`${API_URL}/base-schedule/toggle`, {
      teacher_id: teacherId,
      day,
      period
    });
  }
}
