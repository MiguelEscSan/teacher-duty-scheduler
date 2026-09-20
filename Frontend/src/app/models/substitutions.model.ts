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
  source_type: string | null;
  staff_room_keeper_name: string | null;
  email_notification_dispatched: boolean;
  details: string;
}
