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
}

export interface Absence {
  id?: number;
  teacher_id: string;
  teacher_name?: string;
  date: string;       // Formato ISO: "YYYY-MM-DD"
  period: number;
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
