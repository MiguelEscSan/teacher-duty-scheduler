import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DutySlot, Teacher } from '../../models/schedule.model';
import { TeachersService } from '../../services/teachers.service';

@Component({
  selector: 'app-duty-calendar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './duty-calendar.component.html',
  styleUrls: ['./duty-calendar.component.css']
})
export class DutyCalendarComponent implements OnInit {
  private api = inject(TeachersService);

  dutySlots: DutySlot[] = [];
  isLoading = false;
  errorMessage = '';

  readonly days = [0, 1, 2, 3, 4];
  readonly dayNames = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];
  readonly hours = [
    '08:00 - 09:00', '09:00 - 10:00', '10:00 - 11:00',
    '11:00 - 12:00', '12:00 - 13:00', '13:00 - 14:00'
  ];

  ngOnInit(): void {
    this.loadCalendar();
  }

  loadCalendar(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.api.getDutyTeachers().subscribe({
      next: (slots) => {
        this.dutySlots = slots;
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = err?.error?.detail || 'Error al cargar el calendario de guardias.';
        this.isLoading = false;
      }
    });
  }

  getDutySlot(day: number, period: number): DutySlot | undefined {
    return this.dutySlots.find((slot) =>
      slot.day_of_week === day && slot.period === period
    );
  }

  getDutyTeachers(day: number, period: number): Teacher[] {
    return this.getDutySlot(day, period)?.teachers ?? [];
  }
}
