export interface Teacher {
  id?: string;
  name: string;
  department: string;
}

export interface TeacherRank {
  id: string;
  name: string;
  department: string;
  count: number;
}

export interface BaseSlot {
  day: number;
  period: number;
  status: 'FREE' | 'TEACHING';
  group_id: string | null;
  group_name: string | null;
}

export interface StudentGroup {
  id: string;
  name: string;
  student_count: number | null;
}

export interface Absence {
  id?: number;
  teacher_id: string;
  teacher_name?: string;
  date: string;       // YYYY-MM-DD
  all_day?: boolean;  // Flag para el formulario
  period: number;
  group_name?: string;
  student_count?: number | null;
  reason: string;
}

export interface DayMetadata {
  day_index: number;
  day_name: string;
  date: string;       // "YYYY-MM-DD"
  formatted: string;  // "Lunes 21 Sep"
}

export interface GridCell {
  date: string;
  day_index: number;
  period: number;
  assigned: string[];
  deficit: number;
}

export interface OptimizationResponse {
  status: string;
  is_optimal: boolean;
  total_deficits: number;
  max_difference: number;
  week_label: string;
  days: DayMetadata[];
  grid: GridCell[][];
  ranking: TeacherRank[];
  incidents: string[];
}

export interface AvailableTeacher {
  id: string;
  name: string;
  department: string;
  duty_type: 'FIXED_DUTY' | 'SHORT_TERM' | 'FREE';
  interventions_count: number;
}

export interface DutySlot {
  day_of_week: number;
  day_name: string;
  period: number;
  teachers: Teacher[];
}

export interface ManualAssignmentPayload {
  date: string;          // 'YYYY-MM-DD'
  period: number;        // 0 a 5
  absent_teacher_id: string;
  substitute_teacher_id: string;
  group_id?: string;
  notes?: string;
}
