import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { GuardiasService } from '../../services/shift.services';
import { BaseSlot, StudentGroup, Teacher } from '../../models/schedule.model';

@Component({
  selector: 'app-teachers',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './teachers.component.html',
  styleUrls: ['./teachers.component.css']
})
export class TeachersComponent implements OnInit {
  private api = inject(GuardiasService);

  teachers: Teacher[] = [];
  groups: StudentGroup[] = [];
  selectedTeacher: Teacher | null = null;
  teacherSchedule: BaseSlot[][] = [];

  // Control del modal de asignación de grupo
  activeSlot: BaseSlot | null = null;
  selectedGroupId: string = '';

  newTeacher: { name: string; department: string } = {
    name: '',
    department: 'Matemáticas'
  };

  departments = [
    'Matemáticas', 'Lengua Castellana y Literatura', 'Inglés / Idiomas',
    'Ciencias Naturales / Física y Química', 'Geografía e Historia',
    'Educación Física', 'Tecnología e Informática', 'Música',
    'Artes Plásticas y Dibujo', 'Orientación Educativa', 'Filosofía'
  ];

  isLoadingSchedule = false;
  days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];
  hours = [
    '08:00 - 09:00', '09:00 - 10:00', '10:00 - 11:00',
    '11:00 - 12:00', '12:00 - 13:00', '13:00 - 14:00'
  ];

  ngOnInit(): void {
    this.loadTeachers();
    this.api.getGroups().subscribe(g => this.groups = g);
  }

  loadTeachers(): void {
    this.api.getTeachers().subscribe(t => {
      this.teachers = t;
      if (!this.selectedTeacher && t.length > 0) {
        this.selectTeacher(t[0]);
      }
    });
  }

  selectTeacher(teacher: Teacher): void {
    this.selectedTeacher = teacher;
    this.isLoadingSchedule = true;
    this.api.getBaseSchedule(teacher.id!).subscribe({
      next: (schedule) => {
        this.teacherSchedule = schedule;
        this.isLoadingSchedule = false;
      },
      error: () => this.isLoadingSchedule = false
    });
  }

  // Al hacer clic en una casilla, se abre el selector de grupo
  openSlotModal(cell: BaseSlot): void {
    this.activeSlot = cell;
    this.selectedGroupId = cell.group_id || (this.groups.length > 0 ? this.groups[0].id : '');
  }

  closeModal(): void {
    this.activeSlot = null;
  }

  confirmGroupAssignment(): void {
    if (!this.selectedTeacher?.id || !this.activeSlot) return;

    this.api.assignSlotGroup(
      this.selectedTeacher.id,
      this.activeSlot.day,
      this.activeSlot.period,
      this.selectedGroupId
    ).subscribe(() => {
      this.selectTeacher(this.selectedTeacher!);
      this.closeModal();
    });
  }

  setSlotFree(): void {
    if (!this.selectedTeacher?.id || !this.activeSlot) return;

    this.api.assignSlotGroup(
      this.selectedTeacher.id,
      this.activeSlot.day,
      this.activeSlot.period,
      null
    ).subscribe(() => {
      this.selectTeacher(this.selectedTeacher!);
      this.closeModal();
    });
  }

  saveTeacher(): void {
    if (!this.newTeacher.name.trim()) return;
    this.api.addTeacher({
      name: this.newTeacher.name.trim(),
      department: this.newTeacher.department
    }).subscribe((created) => {
      this.newTeacher.name = '';
      this.teachers.push(created);
      this.selectTeacher(created);
    });
  }

  removeTeacher(id: string): void {
    if (!confirm('¿Eliminar a este docente?')) return;
    this.api.deleteTeacher(id).subscribe(() => {
      this.teachers = this.teachers.filter(t => t.id !== id);
      this.selectedTeacher = this.teachers.length > 0 ? this.teachers[0] : null;
      if (this.selectedTeacher) this.selectTeacher(this.selectedTeacher);
    });
  }
}
