import { AfterViewInit, Component, ElementRef, EventEmitter, HostListener, Input, Output, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { StudentGroup } from '../../../../models/schedule.model';

@Component({
  selector: 'app-delete-group-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './delete-group-modal.component.html',
  styleUrls: ['./delete-group-modal.component.css']
})
export class DeleteGroupModalComponent implements AfterViewInit {
  @Input({ required: true }) group!: StudentGroup;
  @Input() isLoading = false;
  @Output() confirmed = new EventEmitter<void>();
  @Output() cancelled = new EventEmitter<void>();
  @ViewChild('confirmButton') private confirmButton?: ElementRef<HTMLButtonElement>;

  ngAfterViewInit(): void {
    setTimeout(() => this.confirmButton?.nativeElement.focus());
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {
    if (!this.isLoading) this.cancelled.emit();
  }

  @HostListener('document:keydown', ['$event'])
  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Tab') {
      const focusable = Array.from(document.querySelectorAll<HTMLButtonElement>(
        '.delete-modal button:not([disabled])'
      ));
      if (focusable.length && (event.target === focusable[0] && event.shiftKey || event.target === focusable[focusable.length - 1] && !event.shiftKey)) {
        event.preventDefault();
        focusable[event.shiftKey ? focusable.length - 1 : 0].focus();
      }
    }
    if (event.key === 'Enter' && event.target === document.body) {
      event.preventDefault();
      if (!this.isLoading) this.confirmed.emit();
    }
  }
}
