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

  addTeacher(teacher: Pick<Teacher, 'name' | 'department' | 'email'>): Observable<Teacher> {
    return this.http.post<Teacher>(`${API_URL}/teachers`, teacher);
  }

  updateTeacher(id: string, teacher: Pick<Teacher, 'name' | 'department' | 'email'>): Observable<Teacher> {
    return this.http.put<Teacher>(`${API_URL}/teachers/${id}`, teacher);
  }

  deleteTeacher(id: string): Observable<any> {
    return this.http.delete(`${API_URL}/teachers/${id}`);
  }

}
