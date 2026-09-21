import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-teacher-form-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './teacher-form-modal.component.html',
  styleUrls: ['./teacher-form-modal.component.css']
})
export class TeacherFormModalComponent {
  @Input() teacher = { name: '', department: 'Matemáticas' };
  @Input() departments: string[] = [];
  @Output() saved = new EventEmitter<void>();
  @Output() cancelled = new EventEmitter<void>();

  submit(): void {
    if (this.teacher.name.trim()) this.saved.emit();
  }

  close(): void {
    this.cancelled.emit();
  }
}
