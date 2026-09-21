import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Teacher } from '../../../../models/schedule.model';

@Component({
  selector: 'app-absence-form-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './absence-form-modal.component.html',
  styleUrls: ['./absence-form-modal.component.css']
})
export class AbsenceFormModalComponent {
  @Input() teachers: Teacher[] = [];
  @Input() absence = {
    teacher_id: '',
    date: new Date().toISOString().split('T')[0],
    all_day: true,
    period: 0,
    reason: 'Baja médica / Permiso',
    resolved: false
  };
  @Input() hours: string[] = [];

  @Output() saved = new EventEmitter<void>();
  @Output() cancelled = new EventEmitter<void>();

  submit(): void {
    if (!this.absence.teacher_id || !this.absence.date) return;
    this.saved.emit();
  }

  close(): void {
    this.cancelled.emit();
  }
}
