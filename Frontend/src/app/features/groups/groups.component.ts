import { CommonModule } from '@angular/common';
import { Component, HostListener, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BaseScheduleService } from '../../services/base-schedule.service';
import { StudentGroup } from '../../models/schedule.model';
import { DeleteGroupModalComponent } from './components/delete-group-modal/delete-group-modal.component';

@Component({
  selector: 'app-groups',
  standalone: true,
  imports: [CommonModule, FormsModule, DeleteGroupModalComponent],
  templateUrl: './groups.component.html',
  styleUrls: ['./groups.component.css']
})
export class GroupsComponent implements OnInit {
  private api = inject(BaseScheduleService);
  groups: StudentGroup[] = [];
  loading = false;
  editing: StudentGroup | null = null;
  form = { name: '', student_count: null as number | null };
  errorMessage = '';
  toastMessage = '';
  showModal = false;
  groupToDelete: StudentGroup | null = null;
  deletingGroupId: string | null = null;
  openActionsGroupId: string | null = null;

  ngOnInit(): void { this.load(); }
  @HostListener('document:click')
  closeActionsMenu(): void { this.openActionsGroupId = null; }
  load(): void {
    this.loading = true;
    this.api.getGroups().subscribe({ next: groups => { this.groups = groups; this.loading = false; }, error: err => { this.errorMessage = err?.error?.detail || 'No se pudieron cargar los grupos.'; this.loading = false; } });
  }
  open(group?: StudentGroup): void { this.openActionsGroupId = null; this.editing = group || null; this.form = group ? { name: group.name, student_count: group.student_count } : { name: '', student_count: null }; this.showModal = true; }
  close(): void { this.editing = null; this.showModal = false; }
  save(): void {
    if (!this.form.name.trim() || (this.form.student_count !== null && this.form.student_count < 0)) return;
    const request = this.editing ? this.api.updateGroup(this.editing.id, this.form) : this.api.createGroup(this.form);
    request.subscribe({ next: () => { this.close(); this.load(); this.toastMessage = 'Grupo guardado correctamente.'; }, error: err => this.errorMessage = err?.error?.detail || 'No se pudo guardar el grupo.' });
  }

  toggleActions(groupId: string): void {
    this.openActionsGroupId = this.openActionsGroupId === groupId ? null : groupId;
  }

  requestDelete(group: StudentGroup): void {
    this.openActionsGroupId = null;
    this.groupToDelete = group;
  }

  cancelDelete(): void {
    if (!this.deletingGroupId) this.groupToDelete = null;
  }

  confirmDelete(): void {
    const group = this.groupToDelete;
    if (!group || this.deletingGroupId) return;
    this.deletingGroupId = group.id;
    this.api.deleteGroup(group.id).subscribe({
      next: () => {
        this.groups = this.groups.filter(item => item.id !== group.id);
        this.groupToDelete = null;
        this.deletingGroupId = null;
        this.toastMessage = `Grupo ${group.name} eliminado. Las franjas lectivas asociadas han quedado libres.`;
      },
      error: err => {
        this.errorMessage = err?.error?.detail || err?.response?.data?.detail || 'No se pudo eliminar el grupo.';
        this.deletingGroupId = null;
      }
    });
  }
}
