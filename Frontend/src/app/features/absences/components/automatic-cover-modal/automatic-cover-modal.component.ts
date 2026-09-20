import { Component, EventEmitter, Input, OnInit, Output, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GuardiasService } from '../../../../services/shift.services';
import { Absence } from '../../../../models/schedule.model';
import { PeriodResolveResponse } from '../../../../models/substitutions.model';

@Component({
  selector: 'app-automatic-cover-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './automatic-cover-modal.component.html',
  styleUrls: ['./automatic-cover-modal.component.css']
})
export class AutomaticCoverModalComponent implements OnInit {
  @Input() absence!: Absence;
  @Output() confirmed = new EventEmitter<void>();
  @Output() cancelled = new EventEmitter<void>();

  private guardiasService = inject(GuardiasService);

  resolution: PeriodResolveResponse | null = null;
  loading = true;
  sendingEmail = false;
  emailSent = false;
  errorMsg = '';

  ngOnInit(): void {
    this.resolve();
  }

  resolve(): void {
    this.loading = true;
    this.errorMsg = '';
    this.resolution = null;

    this.guardiasService.resolvePeriod({
      date: this.absence.date,
      period: this.absence.period,
      absent_teacher_id: this.absence.teacher_id,
      group_id: this.absence.group_id,
      action: 'AUTO_ASSIGN'
    }).subscribe({
      next: (response) => {
        this.resolution = response;
        this.loading = false;
      },
      error: (err) => {
        console.error(err);
        this.errorMsg = 'No se pudo resolver automáticamente la sustitución.';
        this.loading = false;
      }
    });
  }

  sendEmail(): void {
    if (!this.resolution?.resolved || !this.resolution.substitute_id) return;

    this.sendingEmail = true;
    this.guardiasService.sendSubstitutionEmail({
      date: this.absence.date,
      period: this.absence.period,
      absent_teacher_id: this.absence.teacher_id,
      substitute_teacher_id: this.resolution.substitute_id,
      group_id: this.absence.group_id
    }).subscribe({
      next: () => {
        this.sendingEmail = false;
        this.emailSent = true;
      },
      error: (err) => {
        console.error(err);
        this.sendingEmail = false;
        this.errorMsg = 'No se pudo enviar el correo al profesor sustituto.';
      }
    });
  }

  close(): void {
    this.cancelled.emit();
  }
}
