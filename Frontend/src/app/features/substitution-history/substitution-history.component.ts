import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { GuardiasService } from '../../services/shift.services';
import { SubstitutionHistory } from '../../models/substitutions.model';
import { Teacher } from '../../models/schedule.model';

@Component({
  selector: 'app-substitution-history',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './substitution-history.component.html',
  styleUrls: ['./substitution-history.component.css']
})
export class SubstitutionHistoryComponent implements OnInit {
  private api = inject(GuardiasService);

  history: SubstitutionHistory[] = [];
  teachers: Teacher[] = [];
  loading = false;
  errorMessage = '';
  filters = {
    date: '',
    substitute_teacher_id: '',
    absent_teacher_id: ''
  };

  ngOnInit(): void {
    this.api.getTeachers().subscribe({
      next: teachers => this.teachers = teachers,
      error: () => this.errorMessage = 'No se pudo cargar la lista de profesores.'
    });
    this.loadHistory();
  }

  loadHistory(): void {
    this.loading = true;
    this.errorMessage = '';
    this.api.getSubstitutionHistory(this.filters).subscribe({
      next: history => {
        this.history = history;
        this.loading = false;
      },
      error: () => {
        this.history = [];
        this.loading = false;
        this.errorMessage = 'No se pudo cargar el histórico de sustituciones.';
      }
    });
  }

  clearFilters(): void {
    this.filters = {
      date: '',
      substitute_teacher_id: '',
      absent_teacher_id: ''
    };
    this.loadHistory();
  }

  formatDateTime(value: string): string {
    return new Date(value).toLocaleString('es-ES', {
      dateStyle: 'short',
      timeStyle: 'short'
    });
  }

  sourceLabel(source: string): string {
    const labels: Record<string, string> = {
      FIXED_DUTY: 'Guardia fija',
      ORDINARY_GUARD: 'Guardia Normal',
      SHORT_TERM_SUBSTITUTION: 'Sustitución corta',
      FREE: 'Hora libre',
      MANUAL: 'Manual'
    };
    return labels[source] || source;
  }
}
