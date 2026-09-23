import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DutySlot, Teacher } from '../../models/schedule.model';
import { TeachersService } from '../../services/teachers.service';

@Component({
  selector: 'app-short-term-calendar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './short-term-calendar.component.html',
  styleUrls: ['./short-term-calendar.component.css']
})
export class ShortTermCalendarComponent implements OnInit {
  private api = inject(TeachersService);

  slots: DutySlot[] = [];
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
}
