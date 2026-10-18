import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { EmailSettingsService } from '../../services/email-settings.service';
import {
  EMAIL_TEMPLATE_PLACEHOLDERS,
  EmailSettingsSource,
  EmailSettingsUpdate,
} from '../../models/email-settings.model';

@Component({
  selector: 'app-email-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './email-settings.component.html',
  styleUrls: ['./email-settings.component.css'],
})
export class EmailSettingsComponent implements OnInit {
  private readonly api = inject(EmailSettingsService);

  readonly placeholders = EMAIL_TEMPLATE_PLACEHOLDERS;
  source: EmailSettingsSource = 'none';
  hasPassword = false;
  loading = false;
  saving = false;
  testing = false;
  testRecipient = '';
  errorMessage = '';
  toastMessage = '';

  form: EmailSettingsUpdate = {
    smtp_host: '',
    smtp_port: 587,
    smtp_user: '',
    sender_email: '',
    smtp_password: '',
    subject_template: '',
    body_template: '',
  };

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.api.getSettings().subscribe({
      next: settings => {
        this.source = settings.source;
        this.hasPassword = settings.has_password;
        this.form = {
          smtp_host: settings.smtp_host,
          smtp_port: settings.smtp_port,
          smtp_user: settings.smtp_user,
          sender_email: settings.sender_email,
          smtp_password: '',
          subject_template: settings.subject_template,
          body_template: settings.body_template,
        };
        this.loading = false;
      },
      error: err => {
        this.errorMessage = err?.error?.detail || 'No se pudo cargar la configuración de correo.';
        this.loading = false;
      },
    });
  }

  save(): void {
    this.saving = true;
    this.errorMessage = '';
    this.toastMessage = '';
    this.api.saveSettings({ ...this.form, smtp_password: this.form.smtp_password || null }).subscribe({
      next: settings => {
        this.source = settings.source;
        this.hasPassword = settings.has_password;
        this.form.smtp_password = '';
        this.toastMessage = 'Configuración de correo guardada.';
        this.saving = false;
      },
      error: err => {
        this.errorMessage = err?.error?.detail || 'No se pudo guardar la configuración de correo.';
        this.saving = false;
      },
    });
  }

  sendTest(): void {
    const recipient = this.testRecipient.trim();
    if (!recipient) {
      this.errorMessage = 'Indica un correo de destino para la prueba.';
      return;
    }
    this.testing = true;
    this.errorMessage = '';
    this.toastMessage = '';
    this.api.sendTestEmail(recipient).subscribe({
      next: result => {
        if (result.sent) {
          this.toastMessage = `Correo de prueba enviado a ${recipient}.`;
        } else {
          this.errorMessage = 'No se pudo enviar el correo de prueba. Revisa los datos del servidor.';
        }
        this.testing = false;
      },
      error: err => {
        this.errorMessage = err?.error?.detail || 'No se pudo enviar el correo de prueba.';
        this.testing = false;
      },
    });
  }
}
