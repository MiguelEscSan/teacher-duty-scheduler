import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DutySlot, Teacher } from '../../models/schedule.model';
import { TeachersService } from '../../services/teachers.service';

@Component({
  selector: 'app-short-term-calendar',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './short-term-calendar.component.html',
  styleUrls: ['./short-term-calendar.component.css']
})
export class ShortTermCalendarComponent implements OnInit {
  private api = inject(TeachersService);

  slots: DutySlot[] = [];
  isLoading = false;
  errorMessage = '';
  toastMessage = '';
  selectedSlot: { day: number; period: number } | null = null;
  teacherSearch = '';
  teachers: Teacher[] = [];

  readonly days = [0, 1, 2, 3, 4];
  readonly dayNames = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];
  readonly hours = [
    '08:00 - 09:00', '09:00 - 10:00', '10:00 - 11:00',
    '11:00 - 12:00', '12:00 - 13:00', '13:00 - 14:00'
  ];

  ngOnInit(): void {
    this.api.getTeachers().subscribe({ next: teachers => this.teachers = teachers });
    this.loadCalendar();
  }

  loadCalendar(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.api.getShortTermTeachers().subscribe({
      next: (slots) => {
        this.slots = slots;
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = err?.error?.detail ||
          'Error al cargar el calendario de sustituciones cortas.';
        this.isLoading = false;
      }
    });
  }

  getSlot(day: number, period: number): DutySlot | undefined {
    return this.slots.find((slot) =>
      slot.day_of_week === day && slot.period === period
    );
  }

  getTeachers(day: number, period: number): Teacher[] {
    return this.getSlot(day, period)?.teachers ?? [];
  }

  openAdd(day: number, period: number): void { this.selectedSlot = { day, period }; this.teacherSearch = ''; }
  closeAdd(): void { this.selectedSlot = null; }
  filteredTeachers(): Teacher[] {
    const query = this.teacherSearch.toLowerCase().trim();
    return this.teachers.filter(t => !query || `${t.name} ${t.department}`.toLowerCase().includes(query));
  }
  addTeacher(teacher: Teacher): void {
    if (!this.selectedSlot || !teacher.id) return;
    const slot = this.selectedSlot;
    this.api.assignDuty({ teacher_id: teacher.id, day_of_week: slot.day, period: slot.period, duty_type: 'SHORT_TERM' }).subscribe({
      next: () => { this.toastMessage = `${teacher.name} añadido.`; this.closeAdd(); this.loadCalendar(); },
      error: err => this.errorMessage = err?.error?.detail || 'No se pudo asignar el docente.'
    });
  }
  removeTeacher(teacher: Teacher, day: number, period: number): void {
    if (!teacher.id || !confirm(`¿Quitar a ${teacher.name} de esta franja?`)) return;
    this.api.removeDuty({ teacher_id: teacher.id, day_of_week: day, period, duty_type: 'SHORT_TERM' }).subscribe({
      next: () => { this.toastMessage = `${teacher.name} desasignado.`; this.loadCalendar(); },
      error: err => this.errorMessage = err?.error?.detail || 'No se pudo quitar el docente.'
    });
  }
}
