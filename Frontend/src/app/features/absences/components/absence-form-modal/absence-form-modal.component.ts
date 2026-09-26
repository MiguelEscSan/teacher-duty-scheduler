import { Component, EventEmitter, Input, Output, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Absence, Teacher } from '../../../../models/schedule.model';

@Component({
  selector: 'app-absence-form-modal',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
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
  @Output() bulkSaved = new EventEmitter<Absence[]>();
  @Output() cancelled = new EventEmitter<void>();

  mode: 'simple' | 'bulk' = 'simple';
  teacherSearch = '';
  periods = [0, 1, 2, 3, 4, 5];
  preview: Absence[] = [];
  isSaving = false;
  private fb = inject(FormBuilder);
  bulkForm = this.fb.group({
    teacherIds: this.fb.control<string[]>([], Validators.required),
    startDate: this.fb.control(new Date().toISOString().split('T')[0], [Validators.required, Validators.pattern(/^\d{4}-\d{2}-\d{2}$/)]),
    endDate: this.fb.control(new Date().toISOString().split('T')[0], [Validators.required, Validators.pattern(/^\d{4}-\d{2}-\d{2}$/)]),
    allDay: this.fb.control(true),
    periods: this.fb.control<number[]>([0, 1, 2, 3, 4, 5]),
    reason: this.fb.control('Baja médica', Validators.required)
  });

  submit(): void {
    if (!this.absence.teacher_id || !this.absence.date) return;
    this.saved.emit();
  }

  close(): void {
    this.cancelled.emit();
  }

  get filteredTeachers(): Teacher[] {
    const search = this.teacherSearch.trim().toLowerCase();
    return this.teachers.filter(teacher => !search || teacher.name.toLowerCase().includes(search));
  }

  isTeacherSelected(id?: string): boolean {
    return !!id && (this.bulkForm.controls.teacherIds.value || []).includes(id);
  }

  teacherName(id: string): string {
    return this.teachers.find(teacher => teacher.id === id)?.name || id;
  }

  toggleTeacher(id?: string): void {
    if (!id) return;
    const selected = this.bulkForm.controls.teacherIds.value || [];
    this.bulkForm.controls.teacherIds.setValue(
      selected.includes(id) ? selected.filter((value: string) => value !== id) : [...selected, id]
    );
    this.buildPreview();
  }

  togglePeriod(period: number): void {
    const selected = this.bulkForm.controls.periods.value || [];
    this.bulkForm.controls.periods.setValue(
      selected.includes(period) ? selected.filter((value: number) => value !== period) : [...selected, period]
    );
    this.bulkForm.controls.allDay.setValue(selected.length === 6);
    this.buildPreview();
  }

  setAllDay(allDay: boolean): void {
    this.bulkForm.controls.allDay.setValue(allDay);
    this.bulkForm.controls.periods.setValue(allDay ? [0, 1, 2, 3, 4, 5] : []);
    this.buildPreview();
  }

  buildPreview(): void {
    const value = this.bulkForm.getRawValue();
    const start = value.startDate || '';
    const end = value.endDate || start;
    const periods = value.allDay ? [0, 1, 2, 3, 4, 5] : (value.periods || []);
    const dates: string[] = [];
    if (start && end && start <= end) {
      const cursor = new Date(`${start}T00:00:00`);
      const last = new Date(`${end}T00:00:00`);
      while (cursor <= last) {
        if (cursor.getDay() !== 0 && cursor.getDay() !== 6) dates.push(cursor.toISOString().slice(0, 10));
        cursor.setDate(cursor.getDate() + 1);
      }
    }
    this.preview = (value.teacherIds || []).flatMap((teacherId: string) =>
      dates.flatMap((date: string) => periods.map((period: number) => ({
        teacher_id: teacherId,
        date,
        all_day: false,
        period,
        reason: value.reason || '',
        resolved: false
      })))
    );
  }

  removePreview(index: number): void {
    this.preview.splice(index, 1);
  }

  submitBulk(): void {
    if (this.bulkForm.invalid || this.preview.length === 0) {
      this.bulkForm.markAllAsTouched();
      return;
    }
    this.isSaving = true;
    this.bulkSaved.emit([...this.preview]);
  }
}
