import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { GuardiasService } from '../../services/shift.services';
import { OptimizationResponse } from '../../models/schedule.model';

@Component({
  selector: 'app-guards',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './guards.component.html',
  styleUrls: ['./guards.component.css']
})
export class GuardsComponent implements OnInit {
  private api = inject(GuardiasService);

  selectedDate: string = '';
  results: OptimizationResponse | null = null;
  isOptimizing = false;
  errorMessage = '';

  hours = [
    '08:00 - 09:00', '09:00 - 10:00', '10:00 - 11:00',
    '11:00 - 12:00', '12:00 - 13:00', '13:00 - 14:00'
  ];

  ngOnInit(): void {
    const today = new Date();
    const dayOfWeek = today.getDay(); // 0 = Domingo, 1 = Lunes, ...
    const diffToMonday = today.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1);
    const monday = new Date(today.setDate(diffToMonday));
    this.selectedDate = monday.toISOString().split('T')[0];
    this.calculateGuards();
  }

  changeWeek(deltaDays: number): void {
    const current = new Date(this.selectedDate);
    current.setDate(current.getDate() + deltaDays);
    this.selectedDate = current.toISOString().split('T')[0];
    this.calculateGuards();
  }

  onDateChange(): void {
    this.calculateGuards();
  }

  calculateGuards(): void {
    if (!this.selectedDate) return;
    this.isOptimizing = true;
    this.errorMessage = '';

    this.api.optimizeWeek(this.selectedDate).subscribe({
      next: (res) => {
        this.results = res;
        this.isOptimizing = false;
      },
      error: (err) => {
        this.errorMessage = err?.error?.detail || 'Error al ejecutar el optimizador.';
        this.isOptimizing = false;
      }
    });
  }

  print(): void {
    window.print();
  }
}
