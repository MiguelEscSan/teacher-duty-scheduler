import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DutySlot, Teacher } from '../models/schedule.model';
import { API_URL } from './api-url';

@Injectable({ providedIn: 'root' })
export class TeachersService {
  private readonly http = inject(HttpClient);

  getTeachers(): Observable<Teacher[]> {
    return this.http.get<Teacher[]>(`${API_URL}/teachers`);
  }

  addTeacher(teacher: Teacher): Observable<Teacher> {
    return this.http.post<Teacher>(`${API_URL}/teachers`, teacher);
  }

  deleteTeacher(id: string): Observable<any> {
    return this.http.delete(`${API_URL}/teachers/${id}`);
  }

  getDutyTeachers(): Observable<DutySlot[]> {
    return this.http.get<DutySlot[]>(`${API_URL}/teachers/duty`);
  }

  getShortTermTeachers(): Observable<DutySlot[]> {
    return this.http.get<DutySlot[]>(`${API_URL}/teachers/short-term`);
  }
}
