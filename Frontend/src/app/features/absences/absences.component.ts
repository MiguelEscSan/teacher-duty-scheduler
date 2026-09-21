import { Component, HostListener, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { GuardiasService } from '../../services/shift.services';
import { Absence, Teacher } from '../../models/schedule.model';
import { ManualCoverModalComponent } from './components/manual-cover-modal/manual-cover-modal.component'
import { AutomaticCoverModalComponent } from './components/automatic-cover-modal/automatic-cover-modal.component';

@Component({
  selector: 'app-absences',
  standalone: true,
  imports: [CommonModule, FormsModule, ManualCoverModalComponent, AutomaticCoverModalComponent],
  templateUrl: './absences.component.html',
  styleUrls: ['./absences.component.css']
})
export class AbsencesComponent implements OnInit {
  private api = inject(GuardiasService);

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

  ngOnInit(): void {
    this.api.getTeachers().subscribe(t => {
      this.teachers = t;
      if (t.length > 0) this.newAbsence.teacher_id = t[0].id!;
    });
    this.loadAbsences();
  }

  loadAbsences(): void {
    this.api.getAbsences({
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
    if (!this.newAbsence.teacher_id || !this.newAbsence.date) return;

    this.api.addAbsence(this.newAbsence).subscribe(() => {
      this.loadAbsences();
    });
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

    this.api.markAbsenceAsDoNotCover({
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
    this.api.deleteAbsence(id).subscribe(() => {
      this.loadAbsences();
    });
  }
}
