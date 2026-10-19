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

export interface EmailTemplatePlaceholder {
  /** Nombre que se inserta en la plantilla como {name}. */
  name: string;
  /** Texto que ve el usuario en el botón. */
  label: string;
}

export const EMAIL_TEMPLATE_PLACEHOLDERS: readonly EmailTemplatePlaceholder[] = [
  { name: 'teacher_name', label: 'Docente que cubre' },
  { name: 'absent_teacher_name', label: 'Docente ausente' },
  { name: 'group_name', label: 'Grupo' },
  { name: 'period', label: 'Hora' },
  { name: 'date', label: 'Fecha' },
];
