import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseScheduleService } from '../../services/base-schedule.service';
import { TeachersService } from '../../services/teachers.service';
import { BaseSlot, StudentGroup, Teacher } from '../../models/schedule.model';
import { TeacherFormModalComponent } from './components/teacher-form-modal/teacher-form-modal.component';
import { GroupsComponent } from '../groups/groups.component';
import { ConfirmationModalComponent } from '../../shared/components/confirmation-modal/confirmation-modal.component';

@Component({
  selector: 'app-teachers',
  standalone: true,
  imports: [CommonModule, FormsModule, TeacherFormModalComponent, GroupsComponent, ConfirmationModalComponent],
  templateUrl: './teachers.component.html',
  styleUrls: ['./teachers.component.css']
})
export class TeachersComponent implements OnInit {
  private teachersApi = inject(TeachersService);
  private scheduleApi = inject(BaseScheduleService);

  teachers: Teacher[] = [];
  groups: StudentGroup[] = [];
  selectedTeacher: Teacher | null = null;
  teacherSchedule: BaseSlot[][] = [];
  teacherSearch = '';
  showTeacherModal = false;
  editingTeacherId: string | null = null;
  activeTab: 'teachers' | 'groups' = 'teachers';
  teacherIdToRemove: string | null = null;

  // Control del modal de asignación de grupo
  activeSlot: BaseSlot | null = null;
  selectedGroupId: string = '';
  slotModalStep: 1 | 2 = 1;

  newTeacher: { name: string; department: string; email: string } = {
    name: '',
    department: 'Matemáticas',
    email: ''
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
    this.scheduleApi.getGroups().subscribe(g => this.groups = g);
    this.scheduleApi.groupDeleted$.subscribe(groupId => {
      this.groups = this.groups.filter(group => group.id !== groupId);
      if (this.selectedTeacher) this.selectTeacher(this.selectedTeacher);
    });
  }

  get filteredTeachers(): Teacher[] {
    const search = this.teacherSearch.trim().toLowerCase();
    if (!search) return this.teachers;
    return this.teachers.filter(teacher =>
      teacher.name.toLowerCase().includes(search) ||
      teacher.department.toLowerCase().includes(search)
    );
  }

  get teacherPendingRemoval(): Teacher | null {
    return this.teachers.find(teacher => teacher.id === this.teacherIdToRemove) || null;
  }

  loadTeachers(): void {
    this.teachersApi.getTeachers().subscribe(t => {
      this.teachers = t;
      if (!this.selectedTeacher && t.length > 0) {
        this.selectTeacher(t[0]);
      }
    });
  }

  selectTeacher(teacher: Teacher): void {
    this.selectedTeacher = teacher;
    this.isLoadingSchedule = true;
    this.scheduleApi.getBaseSchedule(teacher.id!).subscribe({
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
    this.slotModalStep = 1;
    this.selectedGroupId = cell.group_id || '';
  }

  closeModal(): void {
    this.activeSlot = null;
    this.slotModalStep = 1;
  }

  chooseTeachingSlot(): void {
    if (this.groups.length === 0) return;
    this.selectedGroupId = this.activeSlot?.group_id || this.groups[0].id;
    this.slotModalStep = 2;
  }

  backToSlotType(): void {
    this.slotModalStep = 1;
  }

  confirmGroupAssignment(): void {
    if (!this.selectedTeacher?.id || !this.activeSlot) return;

    this.scheduleApi.updateSlotStatus(
      this.selectedTeacher.id,
      this.activeSlot.day,
      this.activeSlot.period,
      'TEACHING',
      this.selectedGroupId
    ).subscribe(() => {
      this.selectTeacher(this.selectedTeacher!);
      this.closeModal();
    });
  }

  setSlotFree(): void {
    if (!this.selectedTeacher?.id || !this.activeSlot) return;

    this.scheduleApi.updateSlotStatus(
      this.selectedTeacher.id,
      this.activeSlot.day,
      this.activeSlot.period,
      'FREE'
    ).subscribe(() => {
      this.selectTeacher(this.selectedTeacher!);
      this.closeModal();
    });
  }

  setSlotNonPresential(): void {
    if (!this.selectedTeacher?.id || !this.activeSlot) return;

    this.scheduleApi.updateSlotStatus(
      this.selectedTeacher.id,
      this.activeSlot.day,
      this.activeSlot.period,
      'NON_PRESENTIAL'
    ).subscribe(() => {
      this.selectTeacher(this.selectedTeacher!);
      this.closeModal();
    });
  }

  saveTeacher(): void {
    if (!this.newTeacher.name.trim()) return;
    const payload = {
      name: this.newTeacher.name.trim(),
      department: this.newTeacher.department,
      email: this.newTeacher.email.trim() || undefined
    };
    const request = this.editingTeacherId
      ? this.teachersApi.updateTeacher(this.editingTeacherId, payload)
      : this.teachersApi.addTeacher(payload);
    request.subscribe((saved) => {
      if (this.editingTeacherId) {
        const index = this.teachers.findIndex(t => t.id === saved.id);
        if (index >= 0) this.teachers[index] = saved;
      } else {
        this.teachers.push(saved);
      }
      this.newTeacher = { name: '', department: 'Matemáticas', email: '' };
      this.editingTeacherId = null;
      this.selectTeacher(saved);
      this.showTeacherModal = false;
    });
  }

  openTeacherModal(): void {
    this.editingTeacherId = null;
    this.newTeacher = { name: '', department: 'Matemáticas', email: '' };
    this.showTeacherModal = true;
  }

  openEditTeacherModal(teacher: Teacher): void {
    if (!teacher.id) return;
    this.editingTeacherId = teacher.id;
    this.newTeacher = {
      name: teacher.name,
      department: teacher.department,
      email: teacher.email || ''
    };
    this.showTeacherModal = true;
  }

  closeTeacherModal(): void {
    this.showTeacherModal = false;
    this.editingTeacherId = null;
  }

  removeTeacher(id: string): void {
    this.teacherIdToRemove = id;
  }

  confirmRemoveTeacher(): void {
    const id = this.teacherIdToRemove;
    if (!id) return;

    this.teacherIdToRemove = null;
    this.teachersApi.deleteTeacher(id).subscribe(() => {
      this.teachers = this.teachers.filter(t => t.id !== id);
      this.selectedTeacher = this.teachers.length > 0 ? this.teachers[0] : null;
      if (this.selectedTeacher) this.selectTeacher(this.selectedTeacher);
    });
  }

  cancelRemoveTeacher(): void {
    this.teacherIdToRemove = null;
  }
}
