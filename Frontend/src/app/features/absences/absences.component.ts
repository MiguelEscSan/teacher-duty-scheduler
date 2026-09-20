import { Component, HostListener, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { GuardiasService } from '../../services/shift.services';
import { Absence, Teacher } from '../../models/schedule.model';
import { ManualCoverModalComponent } from './components/manual-cover-modal/manual-cover-modal.component'

@Component({
  selector: 'app-absences',
  standalone: true,
  imports: [CommonModule, FormsModule, ManualCoverModalComponent],
  templateUrl: './absences.component.html',
  styleUrls: ['./absences.component.css']
})
export class AbsencesComponent implements OnInit {
  private api = inject(GuardiasService);

  teachers: Teacher[] = [];
  absences: Absence[] = [];

  newAbsence = {
    teacher_id: '',
    date: new Date().toISOString().split('T')[0],
    all_day: true,
    period: 0,
    reason: 'Baja médica / Permiso'
  };

  hours = [
    '08:00 - 09:00', '09:00 - 10:00', '10:00 - 11:00',
    '11:00 - 12:00', '12:00 - 13:00', '13:00 - 14:00'
  ];

  // Control de menú de 3 puntos y modal
  activeMenuId: number | null = null;
  selectedAbsenceForManualCover: Absence | null = null;

  ngOnInit(): void {
    this.api.getTeachers().subscribe(t => {
      this.teachers = t;
      if (t.length > 0) this.newAbsence.teacher_id = t[0].id!;
    });
    this.loadAbsences();
  }

  loadAbsences(): void {
    this.api.getAbsences().subscribe(a => this.absences = a);
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

  // --- Caso 2: Marcar como no cubrir (Siguiente paso) ---
  markAsDoNotCover(absence: Absence): void {
    this.activeMenuId = null;
    console.log('Caso 2 por implementar:', absence);
  }

  // --- Caso 3: Cubrir automáticamente (Siguiente paso) ---
  resolveAutomatic(absence: Absence): void {
    this.activeMenuId = null;
    console.log('Caso 3 por implementar:', absence);
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
