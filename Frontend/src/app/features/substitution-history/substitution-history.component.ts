import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SubstitutionsService } from '../../services/substitutions.service';
import { TeachersService } from '../../services/teachers.service';
import { SubstitutionHistory } from '../../models/substitutions.model';
import { Teacher } from '../../models/schedule.model';
import { DashboardComponent } from '../dashboard/dashboard.component';

@Component({
  selector: 'app-substitution-history',
  standalone: true,
  imports: [CommonModule, FormsModule, DashboardComponent],
  templateUrl: './substitution-history.component.html',
  styleUrls: ['./substitution-history.component.css']
})
export class SubstitutionHistoryComponent implements OnInit {
  private substitutionsApi = inject(SubstitutionsService);
  private teachersApi = inject(TeachersService);

  history: SubstitutionHistory[] = [];
  teachers: Teacher[] = [];
  loading = false;
  errorMessage = '';
  toastMessage = '';
  editingId: number | string | null = null;
  selectedTeacherId = '';
  activeTab: 'history' | 'balance' = 'history';
  filters = {
    date: '',
    substitute_teacher_id: '',
    absent_teacher_id: ''
  };

  ngOnInit(): void {
    this.teachersApi.getTeachers().subscribe({
      next: teachers => this.teachers = teachers,
      error: () => this.errorMessage = 'No se pudo cargar la lista de profesores.'
    });
    this.loadHistory();
  }

  loadHistory(): void {
    this.loading = true;
    this.errorMessage = '';
    this.substitutionsApi.getSubstitutionHistory(this.filters).subscribe({
      next: history => {
        this.history = history;
        this.loading = false;
      },
      error: () => {
        this.history = [];
        this.loading = false;
        this.errorMessage = 'No se pudo cargar el histórico de sustituciones.';
      }
    });
  }

  clearFilters(): void {
    this.filters = {
      date: '',
      substitute_teacher_id: '',
      absent_teacher_id: ''
    };
    this.loadHistory();
  }

  formatDateTime(value: string): string {
    return new Date(value).toLocaleString('es-ES', {
      dateStyle: 'short',
      timeStyle: 'short'
    });
  }

  sourceLabel(source: string): string {
    const labels: Record<string, string> = {
      FIXED_DUTY: 'Guardia fija',
      ORDINARY_GUARD: 'Guardia Normal',
      SHORT_TERM_SUBSTITUTION: 'Sustitución corta',
      FREE: 'Hora libre',
      MANUAL: 'Manual'
    };
    return labels[source] || source;
  }

  startReassign(item: SubstitutionHistory): void {
    this.editingId = item.id;
    this.selectedTeacherId = item.substitute_teacher_id;
  }

  cancelReassign(): void { this.editingId = null; }

  saveReassign(item: SubstitutionHistory): void {
    if (!this.selectedTeacherId || this.selectedTeacherId === item.absent_teacher_id) {
      this.errorMessage = 'Selecciona un docente distinto del ausente.';
      return;
    }
    this.substitutionsApi.reassignSubstitute(item.id, this.selectedTeacherId).subscribe({
      next: updated => {
        item.substitute_teacher_id = updated.substitute_teacher_id;
        item.substitute_teacher_name = updated.substitute_teacher_name;
        item.source_type = 'MANUAL';
        item.reassigned = true;
        this.editingId = null;
        this.toastMessage = 'Sustituto reasignado correctamente.';
      },
      error: err => this.errorMessage = err?.error?.detail || 'No se pudo reasignar el sustituto.'
    });
  }

  availableTeachers(item: SubstitutionHistory): Teacher[] {
    return this.teachers.filter(t => t.id !== item.absent_teacher_id);
  }
}
