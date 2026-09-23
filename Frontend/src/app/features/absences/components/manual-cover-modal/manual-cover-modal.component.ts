import { Component, EventEmitter, Input, OnInit, Output, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SubstitutionsService } from '../../../../services/substitutions.service';
import {
  AvailableTeacher,
  ManualAssignmentPayload
} from '../../../../models/schedule.model';


@Component({
  selector: 'app-manual-cover-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './manual-cover-modal.component.html',
  styleUrls: ['./manual-cover-modal.component.css']
})
export class ManualCoverModalComponent implements OnInit {
  @Input() absence: any;
  @Output() confirmed = new EventEmitter<void>();
  @Output() cancelled = new EventEmitter<void>();

  private substitutionsApi = inject(SubstitutionsService);

  candidates: AvailableTeacher[] = [];
  selectedTeacher: AvailableTeacher | null = null;
  loading = true;
  submitting = false;
  errorMsg = '';

  ngOnInit(): void {
    this.fetchCandidates();
  }

  fetchCandidates(): void {
    this.loading = true;
    this.errorMsg = '';

    this.substitutionsApi.getAvailableCandidates(this.absence.date, this.absence.period).subscribe({
      next: (data) => {
        this.candidates = data;
        this.loading = false;
      },
      error: (err) => {
        console.error(err);
        this.errorMsg = 'Error al cargar los docentes disponibles en esta franja.';
        this.loading = false;
      }
    });
  }

  selectTeacher(teacher: AvailableTeacher): void {
    this.selectedTeacher = teacher;
  }

  getDutyLabel(type: string): string {
    switch (type) {
      case 'FIXED_DUTY':
        return 'Guardia Ordinaria';
      case 'SHORT_TERM':
        return 'Sust. Corta';
      default:
        return 'Hora Libre';
    }
  }

  confirmAssignment(): void {
    if (!this.selectedTeacher) return;

    this.submitting = true;
    const payload: ManualAssignmentPayload = {
      date: this.absence.date,
      period: this.absence.period,
      absent_teacher_id: this.absence.teacher_id,
      substitute_teacher_id: this.selectedTeacher.id,
      group_id: this.absence.group_id
    };

    this.substitutionsApi.assignManualSubstitution(payload).subscribe({
      next: () => {
        this.submitting = false;
        this.confirmed.emit();
      },
      error: (err) => {
        console.error(err);
        alert('Hubo un error al registrar la sustitución manual.');
        this.submitting = false;
      }
    });
  }

  close(): void {
    this.cancelled.emit();
  }
}
