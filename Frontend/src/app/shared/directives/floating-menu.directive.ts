import { Directive, ElementRef, NgZone, OnDestroy, afterNextRender, inject, input, output } from '@angular/core';

const GAP = 4;
const VIEWPORT_MARGIN = 8;

/**
 * Coloca un menú desplegable con `position: fixed` junto a su botón, para que no
 * lo recorten los contenedores con scroll (p. ej. el envoltorio de una tabla).
 * Se abre hacia arriba si no cabe debajo y emite `menuClose` al hacer scroll o
 * redimensionar la ventana, ya que dejaría de estar alineado con el botón.
 *
 * Uso: <button #trigger ...> <div *ngIf="abierto" [appFloatingMenu]="trigger" (menuClose)="cerrar()">
 */
@Directive({ selector: '[appFloatingMenu]', standalone: true })
export class FloatingMenuDirective implements OnDestroy {
  readonly trigger = input.required<HTMLElement>({ alias: 'appFloatingMenu' });
  readonly menuClose = output<void>();

  private readonly menu: HTMLElement = inject(ElementRef).nativeElement;
  private readonly zone = inject(NgZone);
  private readonly close = () => this.zone.run(() => this.menuClose.emit());

  constructor() {
    this.menu.style.position = 'fixed';
    // Se mide tras renderizar para conocer la altura real del menú (sus opciones pueden variar).
    afterNextRender(() => this.position());
    // En fase de captura para detectar también el scroll de contenedores internos.
    this.zone.runOutsideAngular(() => {
      document.addEventListener('scroll', this.close, true);
      window.addEventListener('resize', this.close);
    });
  }

  ngOnDestroy(): void {
    document.removeEventListener('scroll', this.close, true);
    window.removeEventListener('resize', this.close);
  }

  private position(): void {
    const trigger = this.trigger().getBoundingClientRect();
    const { width, height } = this.menu.getBoundingClientRect();
    const fitsBelow = trigger.bottom + GAP + height <= window.innerHeight - VIEWPORT_MARGIN;
    const fitsAbove = trigger.top - GAP - height >= VIEWPORT_MARGIN;
    const top = !fitsBelow && fitsAbove ? trigger.top - GAP - height : trigger.bottom + GAP;
    // Alineado al borde derecho del botón, sin salirse de la ventana.
    const left = Math.max(VIEWPORT_MARGIN, Math.min(trigger.right - width, window.innerWidth - width - VIEWPORT_MARGIN));

    Object.assign(this.menu.style, { top: `${top}px`, left: `${left}px`, right: 'auto', bottom: 'auto' });
  }
}
