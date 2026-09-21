export interface StudentGroup {
  id: string;
  name: string;
  student_count: number | null;
}

export interface DaySlotPreview {
  period: number;
  group_id: string;
  group_name: string;
  student_count: number | null;
  has_co_teacher: boolean;
  co_teacher_name: string | null;
  requires_action: boolean;
  // Estado local para la UI
  selectedAction?: 'AUTO_ASSIGN' | 'EXCURSION' | 'MERGE_GROUPS' | 'FORCE_SHORT_TERM';
  selectedMergeGroupId?: string;
  isResolved?: boolean;
  resolutionDetails?: string;
}

export interface AbsencePreviewResponse {
  teacher_id: string;
  teacher_name: string;
  date: string;
  day_of_week: number;
  slots: DaySlotPreview[];
}

export interface PeriodResolveResponse {
  date: string;
  period: number;
  resolved: boolean;
  action_applied: string;
  substitute_id: string | null;
  substitute_name: string | null;
  substitute_email: string | null;
  source_type: string | null;
  is_short_term_substitute: boolean;
  is_fixed_duty_substitute: boolean;
  staff_room_keeper_name: string | null;
  email_notification_dispatched: boolean;
  details: string;
}

export interface SubstitutionHistory {
  id: number;
  date: string;
  period: number;
  substitute_teacher_id: string;
  substitute_teacher_name: string;
  absent_teacher_id: string;
  absent_teacher_name: string;
  group_id: string | null;
  group_name: string | null;
  source_type: string;
  created_at: string;
}
