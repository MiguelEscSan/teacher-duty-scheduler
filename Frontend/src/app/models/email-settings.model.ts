export type EmailSettingsSource = 'database' | 'environment' | 'none';

export interface EmailSettings {
  source: EmailSettingsSource;
  smtp_host: string;
  smtp_port: number;
  smtp_user: string;
  sender_email: string;
  has_password: boolean;
  subject_template: string;
  body_template: string;
}

export interface EmailSettingsUpdate extends Omit<EmailSettings, 'source' | 'has_password'> {
  /** Vacía o null: se conserva la contraseña ya guardada. */
  smtp_password: string | null;
}

export const EMAIL_TEMPLATE_PLACEHOLDERS = [
  'teacher_name',
  'absent_teacher_name',
  'group_name',
  'period',
  'date',
] as const;
