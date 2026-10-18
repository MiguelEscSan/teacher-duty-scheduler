export type EmailSettingsSource = 'database' | 'environment' | 'none';

export interface EmailSettings {
  source: EmailSettingsSource;
  smtp_user: string;
  has_password: boolean;
  subject_template: string;
  body_template: string;
}

export interface EmailSettingsUpdate {
  /** Correo con el que se inicia sesión y que también firma como remitente. */
  smtp_user: string;
  /** Vacía o null: se conserva la contraseña ya guardada. */
  smtp_password: string | null;
  subject_template: string;
  body_template: string;
}

export const EMAIL_TEMPLATE_PLACEHOLDERS = [
  'teacher_name',
  'absent_teacher_name',
  'group_name',
  'period',
  'date',
] as const;
