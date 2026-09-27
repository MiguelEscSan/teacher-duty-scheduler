import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SubstitutionsService } from '../../services/substitutions.service';
import { TeachersService } from '../../services/teachers.service';
import { SubstitutionHistory } from '../../models/substitutions.model';
import { Teacher } from '../../models/schedule.model';
import { DashboardComponent } from '../dashboard/dashboard.component';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

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
  private route = inject(ActivatedRoute);

  history: SubstitutionHistory[] = [];
  teachers: Teacher[] = [];
  loading = false;
  errorMessage = '';
  toastMessage = '';
  editingId: number | string | null = null;
  selectedTeacherId = '';
  activeTab: 'history' | 'balance' = 'history';
  filters = {
    date: this.todayDate(),
    substitute_teacher_id: '',
    absent_teacher_id: ''
  };
  selectedIds = new Set<number | string>();
  emailSendingIds = new Set<number | string>();
  emailBatchSending = false;

  ngOnInit(): void {
    this.route.queryParamMap.subscribe(params => {
      const date = params.get('date');
      this.filters.date = date || this.todayDate();
      this.loadHistory();
    });
    const successMessage = history.state?.successMessage as string | undefined;
    if (successMessage) this.toastMessage = successMessage;
    this.teachersApi.getTeachers().subscribe({
      next: teachers => this.teachers = teachers,
      error: () => this.errorMessage = 'No se pudo cargar la lista de profesores.'
    });
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
      date: this.todayDate(),
      substitute_teacher_id: '',
      absent_teacher_id: ''
    };
    this.loadHistory();
  }

  private todayDate(): string {
    const today = new Date();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    return `${today.getFullYear()}-${month}-${day}`;
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

  toggleSelected(id: number | string): void {
    this.selectedIds.has(id) ? this.selectedIds.delete(id) : this.selectedIds.add(id);
  }

  isSelected(id: number | string): boolean { return this.selectedIds.has(id); }

  sendEmail(item: SubstitutionHistory): void {
    if (this.emailSendingIds.has(item.id)) return;
    this.emailSendingIds.add(item.id);
    this.substitutionsApi.sendSubstitutionEmail({
      date: item.date,
      period: item.period,
      absent_teacher_id: item.absent_teacher_id,
      substitute_teacher_id: item.substitute_teacher_id,
      group_id: item.group_id
    }).subscribe({
      next: () => {
        item.notified = true;
        this.toastMessage = `Aviso de guardia programado correctamente para ${item.substitute_teacher_name}.`;
        this.emailSendingIds.delete(item.id);
      },
      error: err => {
        this.errorMessage = err?.error?.detail || 'No se pudo programar el aviso por correo.';
        this.emailSendingIds.delete(item.id);
      }
    });
  }

  sendSelectedEmails(): void {
    const selected = this.history.filter(item => this.selectedIds.has(item.id));
    if (!selected.length || this.emailBatchSending) return;
    this.emailBatchSending = true;
    forkJoin(selected.map(item => this.substitutionsApi.sendSubstitutionEmail({
      date: item.date,
      period: item.period,
      absent_teacher_id: item.absent_teacher_id,
      substitute_teacher_id: item.substitute_teacher_id,
      group_id: item.group_id
    }).pipe(catchError(() => of(null))))).subscribe(results => {
      const sent = results.filter(result => result !== null).length;
      selected.forEach(item => { if (results[selected.indexOf(item)]) item.notified = true; });
      this.toastMessage = `${sent} avisos de guardia programados correctamente.`;
      this.emailBatchSending = false;
      this.selectedIds.clear();
    });
  }
}
