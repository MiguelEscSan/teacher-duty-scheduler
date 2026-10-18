import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { EmailSettings, EmailSettingsUpdate } from '../models/email-settings.model';
import { API_URL } from './api-url';

@Injectable({ providedIn: 'root' })
export class EmailSettingsService {
  private readonly http = inject(HttpClient);

  getSettings(): Observable<EmailSettings> {
    return this.http.get<EmailSettings>(`${API_URL}/email/settings`);
  }

  saveSettings(settings: EmailSettingsUpdate): Observable<EmailSettings> {
    return this.http.put<EmailSettings>(`${API_URL}/email/settings`, settings);
  }

  sendTestEmail(to: string): Observable<{ sent: boolean }> {
    return this.http.post<{ sent: boolean }>(`${API_URL}/email/settings/test`, { to });
  }
}
