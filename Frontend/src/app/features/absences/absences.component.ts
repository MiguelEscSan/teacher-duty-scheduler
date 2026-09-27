import { Component, HostListener, OnInit, inject } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { forkJoin, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { AbsencesService } from '../../services/absences.service';
import { SubstitutionsService } from '../../services/substitutions.service';
import { TeachersService } from '../../services/teachers.service';
import { Absence, Teacher } from '../../models/schedule.model';
import { PeriodResolveResponse } from '../../models/substitutions.model';
import { ManualCoverModalComponent } from './components/manual-cover-modal/manual-cover-modal.component'
import { AutomaticCoverModalComponent } from './components/automatic-cover-modal/automatic-cover-modal.component';
import { AbsenceFormModalComponent } from './components/absence-form-modal/absence-form-modal.component';

@Component({
  selector: 'app-absences',
  standalone: true,
  imports: [CommonModule, FormsModule, ManualCoverModalComponent, AutomaticCoverModalComponent, AbsenceFormModalComponent],
  templateUrl: './absences.component.html',
  styleUrls: ['./absences.component.css']
})
export class AbsencesComponent implements OnInit {
  private absencesApi = inject(AbsencesService);
  private substitutionsApi = inject(SubstitutionsService);
  private teachersApi = inject(TeachersService);
  private router = inject(Router);

  teachers: Teacher[] = [];
  absences: Absence[] = [];
  filters = {
    date: '',
    teacher_id: '',
    status: 'all' as 'all' | 'pending' | 'resolved'
  };

  newAbsence = {
    teacher_id: '',
    date: new Date().toISOString().split('T')[0],
    all_day: true,
    period: 0,
    reason: 'Baja médica / Permiso',
    resolved: false
  };

  hours = [
    '08:00 - 09:00', '09:00 - 10:00', '10:00 - 11:00',
    '11:00 - 12:00', '12:00 - 13:00', '13:00 - 14:00'
  ];

  // Control de menú de 3 puntos y modal
  activeMenuId: number | null = null;
  selectedAbsenceForManualCover: Absence | null = null;
  selectedAbsenceForAutomaticCover: Absence | null = null;
  showAbsenceModal = false;
  errorMessage = '';
  autoCoverLoading = false;
  autoCoverResult: PeriodResolveResponse | null = null;
  bulkFailureMessage = '';
  selectedAbsenceIds = new Set<number>();
  bulkActionLoading = false;

  ngOnInit(): void {
    this.teachersApi.getTeachers().subscribe(t => {
      this.teachers = t;
      if (t.length > 0) this.newAbsence.teacher_id = t[0].id!;
    });
    this.loadAbsences();
  }

  loadAbsences(): void {
    this.absencesApi.getAbsences({
      date: this.filters.date || undefined,
      teacher_id: this.filters.teacher_id || undefined,
      resolved: this.filters.status === 'all' ? undefined : this.filters.status === 'resolved'
    }).subscribe(a => this.absences = a);
  }

  clearFilters(): void {
    this.filters = { date: '', teacher_id: '', status: 'all' };
    this.loadAbsences();
  }

  submitAbsence(): void {
    this.absencesApi.addAbsence(this.newAbsence).subscribe(() => {
      this.loadAbsences();
      this.showAbsenceModal = false;
    });
  }

  openAbsenceModal(): void {
    this.showAbsenceModal = true;
  }

  closeAbsenceModal(): void {
    this.showAbsenceModal = false;
  }

  get selectedAbsences(): Absence[] {
    return this.absences.filter(item => item.id !== undefined && this.selectedAbsenceIds.has(item.id));
  }

  toggleAbsenceSelection(id?: number): void {
    if (id === undefined) return;
    this.selectedAbsenceIds.has(id) ? this.selectedAbsenceIds.delete(id) : this.selectedAbsenceIds.add(id);
  }

  isAbsenceSelected(id?: number): boolean {
    return id !== undefined && this.selectedAbsenceIds.has(id);
  }

  clearAbsenceSelection(): void {
    this.selectedAbsenceIds.clear();
  }

  openBulkManualCover(): void {
    const selected = this.selectedAbsences.filter(item => !item.resolved && !item.is_duty_absence);
    if (!selected.length) return;
    this.selectedAbsenceForManualCover = selected[0];
  }

  markSelectedAsDoNotCover(): void {
    const selected = this.selectedAbsences.filter(item => !item.resolved && !item.is_duty_absence);
    if (!selected.length || this.bulkActionLoading) return;
    this.bulkActionLoading = true;
    forkJoin(selected.map(item => this.substitutionsApi.markAbsenceAsDoNotCover({
      date: item.date, period: item.period, absent_teacher_id: item.teacher_id
    }).pipe(catchError(() => of(null))))).subscribe(results => {
      const failed = results.filter(result => result === null).length;
      this.bulkActionLoading = false;
      this.clearAbsenceSelection();
      this.bulkFailureMessage = failed ? `${selected.length - failed} ausencias marcadas como no cubrir y ${failed} fallaron.` : '';
      this.loadAbsences();
      this.redirectToTodayHistory();
    });
  }

  autoCoverSelected(): void {
    const selected = this.selectedAbsences.filter(item => !item.resolved && !item.is_duty_absence);
    if (!selected.length || this.bulkActionLoading) return;
    this.bulkActionLoading = true;
    forkJoin(selected.map(item => this.substitutionsApi.resolvePeriod({
      date: item.date,
      period: item.period,
      absent_teacher_id: item.teacher_id,
      group_id: item.group_id,
      action: 'AUTO_ASSIGN'
    }).pipe(catchError(() => of(null))))).subscribe(results => {
      const failed = results.filter(result => result === null).length;
      this.bulkActionLoading = false;
      this.clearAbsenceSelection();
      this.bulkFailureMessage = failed ? `${selected.length - failed} ausencias auto-cubiertas y ${failed} fallaron.` : '';
      this.loadAbsences();
      this.redirectToTodayHistory();
    });
  }

  redirectToTodayHistory(): void {
    this.router.navigate(['/substitutions/history'], {
      queryParams: { date: new Date().toISOString().slice(0, 10) }
    });
  }

  submitBulkAbsences(absences: Absence[]): void {
    const results = absences.map(absence =>
      this.absencesApi.addAbsence(absence).pipe(
        map(() => ({ success: true, absence, message: '' })),
        catchError(error => of({ success: false, absence, message: error?.error?.detail || 'Error de validación' }))
      )
    );
    forkJoin(results).subscribe(responses => {
      const failures = responses.filter(response => !response.success);
      const saved = responses.length - failures.length;
      this.showAbsenceModal = false;
      this.bulkFailureMessage = failures.length
        ? `${saved} ausencias guardadas. ${failures.length} no se pudieron registrar: ${failures.map(item => `${item.absence.date} P${item.absence.period} (${this.teacherName(item.absence.teacher_id)}): ${item.message}`).join('; ')}`
        : '';
      this.loadAbsences();
      if (!failures.length) {
        this.router.navigate(['/substitutions/history'], {
          queryParams: { date: absences[0]?.date },
          state: { successMessage: `${saved} ausencias registradas correctamente. Redirigiendo al seguimiento de sustituciones...` }
        });
      }
    });
  }

  teacherName(id: string): string {
    return this.teachers.find(teacher => teacher.id === id)?.name || id;
  }

  goToBulkHistory(): void {
    this.router.navigate(['/substitutions/history'], { queryParams: { date: this.filters.date || undefined } });
  }

  // Cierra cualquier menú desplegable si el usuario pulsa en cualquier parte de la pantalla
  @HostListener('document:click')
  onDocumentClick(): void {
    this.activeMenuId = null;
  }

  toggleMenu(event: MouseEvent, absenceId?: number): void {
    event.stopPropagation();
    if (absenceId === undefined) return;
    this.activeMenuId = this.activeMenuId === absenceId ? null : absenceId;
  }

  // --- Caso 1: Cubrir Manualmente ---
  openManualCoverModal(absence: Absence): void {
    if (absence.resolved) return;
    this.activeMenuId = null;
    this.selectedAbsenceForManualCover = absence;
  }

  onManualCoverConfirmed(substituteTeacherId: string): void {
    const wasBulk = this.selectedAbsenceIds.size > 1;
    if (wasBulk) {
      const selected = this.selectedAbsences;
      this.bulkActionLoading = true;
      forkJoin(selected.map(item => this.substitutionsApi.assignManualSubstitution({
        date: item.date,
        period: item.period,
        absent_teacher_id: item.teacher_id,
        substitute_teacher_id: substituteTeacherId,
        group_id: item.group_id
      }).pipe(catchError(() => of(null))))).subscribe(results => {
        const failed = results.filter(result => result === null).length;
        this.bulkActionLoading = false;
        this.bulkFailureMessage = failed ? `${selected.length - failed} sustituciones registradas y ${failed} fallaron.` : '';
        this.selectedAbsenceForManualCover = null;
        this.clearAbsenceSelection();
        this.loadAbsences();
        if (!failed) this.redirectToTodayHistory();
      });
      return;
    }
    this.selectedAbsenceForManualCover = null;
    this.clearAbsenceSelection();
    this.loadAbsences(); // Recarga la tabla para reflejar la sustitución
    if (wasBulk) this.redirectToTodayHistory();
  }

  onManualCoverCancelled(): void {
    this.selectedAbsenceForManualCover = null;
  }

  markAsDoNotCover(absence: Absence): void {
    this.activeMenuId = null;
    if (absence.resolved) return;

    this.substitutionsApi.markAbsenceAsDoNotCover({
      date: absence.date,
      period: absence.period,
      absent_teacher_id: absence.teacher_id
    }).subscribe(() => {
      this.loadAbsences();
    });
  }

  resolveAutomatic(absence: Absence): void {
    if (absence.resolved) return;
    this.activeMenuId = null;
    this.selectedAbsenceForAutomaticCover = absence;
  }

  autoCoverDuties(absence: Absence): void {
    if (!absence.teacher_id) return;
    this.autoCoverLoading = true;
    this.substitutionsApi.resolvePeriod({
      date: absence.date,
      period: absence.period,
      absent_teacher_id: absence.teacher_id,
      group_id: absence.group_id,
      action: 'AUTO_ASSIGN'
    }).subscribe({
      next: result => { this.autoCoverResult = result; this.autoCoverLoading = false; this.loadAbsences(); },
      error: err => { this.errorMessage = err?.error?.detail || 'No se pudo resolver automáticamente la sustitución.'; this.autoCoverLoading = false; }
    });
  }

  closeAutoCoverResult(): void { this.autoCoverResult = null; }

  onAutomaticCoverConfirmed(): void {
    this.selectedAbsenceForAutomaticCover = null;
    this.loadAbsences();
  }

  onAutomaticCoverCancelled(): void {
    this.selectedAbsenceForAutomaticCover = null;
  }

  // --- Caso 4: Eliminar ausencia (Ya implementado) ---
  remove(id?: number): void {
    this.activeMenuId = null;
    if (id === undefined) return;
    this.absencesApi.deleteAbsence(id).subscribe(() => {
      this.loadAbsences();
    });
  }
}
