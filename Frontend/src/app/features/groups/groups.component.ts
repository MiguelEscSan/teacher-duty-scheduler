import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BaseScheduleService } from '../../services/base-schedule.service';
import { StudentGroup } from '../../models/schedule.model';

@Component({
  selector: 'app-groups',
  standalone: true,
  imports: [CommonModule, FormsModule],
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

  ngOnInit(): void { this.load(); }
  load(): void {
    this.loading = true;
    this.api.getGroups().subscribe({ next: groups => { this.groups = groups; this.loading = false; }, error: err => { this.errorMessage = err?.error?.detail || 'No se pudieron cargar los grupos.'; this.loading = false; } });
  }
  open(group?: StudentGroup): void { this.editing = group || null; this.form = group ? { name: group.name, student_count: group.student_count } : { name: '', student_count: null }; this.showModal = true; }
  close(): void { this.editing = null; this.showModal = false; }
  save(): void {
    if (!this.form.name.trim() || (this.form.student_count !== null && this.form.student_count < 0)) return;
    const request = this.editing ? this.api.updateGroup(this.editing.id, this.form) : this.api.createGroup(this.form);
    request.subscribe({ next: () => { this.close(); this.load(); this.toastMessage = 'Grupo guardado correctamente.'; }, error: err => this.errorMessage = err?.error?.detail || 'No se pudo guardar el grupo.' });
  }
}
