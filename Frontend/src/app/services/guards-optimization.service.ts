import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { OptimizationResponse } from '../models/schedule.model';
import { API_URL } from './api-url';

@Injectable({ providedIn: 'root' })
export class GuardsOptimizationService {
  private readonly http = inject(HttpClient);

  optimizeWeek(startDate: string): Observable<OptimizationResponse> {
    return this.http.post<OptimizationResponse>(`${API_URL}/guards/optimize`, {
      start_date: startDate
    });
  }
}
