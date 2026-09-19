import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { GuardiasService } from '../../services/shift.services';
import { Absence, Teacher } from '../../models/schedule.model';

@Component({
  selector: 'app-absences',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './absences.component.html',
  styleUrls: ['./absences.component.css']
})
export class AbsencesComponent implements OnInit {
  private api = inject(GuardiasService);

  teachers: Teacher[] = [];
  absences: Absence[] = [];

  newAbsence: Absence = {
    teacher_id: '',
    date: new Date().toISOString().split('T')[0], // Fecha de hoy por defecto
    period: 0,
    reason: 'Permiso puntual / Baja'
  };

  hours = [
    '08:00 - 09:00', '09:00 - 10:00', '10:00 - 11:00',
    '11:00 - 12:00', '12:00 - 13:00', '13:00 - 14:00'
  ];

  ngOnInit(): void {
    this.api.getTeachers().subscribe(t => {
      this.teachers = t;
      if (t.length > 0) this.newAbsence.teacher_id = <string>t[0].id;
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

  remove(id?: number): void {
    if (id === undefined) return;
    this.api.deleteAbsence(id).subscribe(() => {
      this.loadAbsences();
    });
  }
}
