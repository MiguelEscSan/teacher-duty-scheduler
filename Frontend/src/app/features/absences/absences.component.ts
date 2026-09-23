import { Component, HostListener, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AbsencesService } from '../../services/absences.service';
import { SubstitutionsService } from '../../services/substitutions.service';
import { TeachersService } from '../../services/teachers.service';
import { Absence, Teacher } from '../../models/schedule.model';
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

  onManualCoverConfirmed(): void {
    this.selectedAbsenceForManualCover = null;
    this.loadAbsences(); // Recarga la tabla para reflejar la sustitución
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
