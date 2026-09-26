import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { SubstitutionsService } from '../../services/substitutions.service';
import { SubstitutionSummary } from '../../models/schedule.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  private api = inject(SubstitutionsService);
  rows: SubstitutionSummary[] = [];
  query = '';
  sortKey: keyof SubstitutionSummary = 'total_interventions';
  ascending = false;
  max = 1;
  ngOnInit(): void { this.api.getSummary().subscribe({ next: rows => { this.rows = rows; this.max = Math.max(1, ...rows.map(r => r.total_interventions)); } }); }
  get filtered(): SubstitutionSummary[] {
    const q = this.query.toLowerCase();
    return [...this.rows].filter(r => r.teacher_name.toLowerCase().includes(q)).sort((a,b) => {
      const av = a[this.sortKey] as number | string, bv = b[this.sortKey] as number | string;
      return (av < bv ? -1 : av > bv ? 1 : 0) * (this.ascending ? 1 : -1);
    });
  }
  sort(key: keyof SubstitutionSummary): void { this.ascending = this.sortKey === key ? !this.ascending : false; this.sortKey = key; }
  exportCsv(): void {
    const csv = ['Docente,Guardias ordinarias,Sustituciones cortas,Manuales,Total', ...this.filtered.map(r => `"${r.teacher_name}",${r.ordinary_guard_count},${r.short_term_count},${r.manual_count},${r.total_interventions}`)].join('\n');
    const link = document.createElement('a'); link.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' })); link.download = 'balance-intervenciones.csv'; link.click(); URL.revokeObjectURL(link.href);
  }
}
