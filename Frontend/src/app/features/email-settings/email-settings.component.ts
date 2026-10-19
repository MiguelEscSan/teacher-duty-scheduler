import { Component, ElementRef, OnInit, ViewChild, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { EmailSettingsService } from '../../services/email-settings.service';
import {
  EMAIL_TEMPLATE_PLACEHOLDERS,
  EmailSettingsSource,
  EmailSettingsUpdate,
} from '../../models/email-settings.model';

type TemplateField = 'subject_template' | 'body_template';

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
  @ViewChild('subjectInput') private subjectInput?: ElementRef<HTMLInputElement>;
  @ViewChild('bodyInput') private bodyInput?: ElementRef<HTMLTextAreaElement>;
  /** Último campo de plantilla con foco: ahí se insertan las variables. */
  activeField: TemplateField = 'body_template';
  source: EmailSettingsSource = 'none';
  hasPassword = false;
  loading = false;
  saving = false;
  testing = false;
  testRecipient = '';
  errorMessage = '';
  toastMessage = '';

  form: EmailSettingsUpdate = {
    smtp_user: '',
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
          smtp_user: settings.smtp_user,
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

  focusField(field: TemplateField): void {
    this.activeField = field;
  }

  /** Inserta {nombre} en la posición del cursor del campo activo. */
  insertPlaceholder(name: string): void {
    const field = this.activeField;
    const element = field === 'subject_template' ? this.subjectInput?.nativeElement : this.bodyInput?.nativeElement;
    const token = `{${name}}`;
    const current = this.form[field];
    const start = element?.selectionStart ?? current.length;
    const end = element?.selectionEnd ?? current.length;

    this.form[field] = current.slice(0, start) + token + current.slice(end);

    // Tras actualizar el modelo, devolvemos el foco y colocamos el cursor después del token.
    setTimeout(() => {
      if (!element) return;
      element.focus();
      const caret = start + token.length;
      element.setSelectionRange(caret, caret);
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
