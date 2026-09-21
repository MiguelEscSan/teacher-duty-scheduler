import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-calendar-layout',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './calendar-layout.component.html',
  styleUrls: ['./calendar-layout.component.css']
})
export class CalendarLayoutComponent {}
