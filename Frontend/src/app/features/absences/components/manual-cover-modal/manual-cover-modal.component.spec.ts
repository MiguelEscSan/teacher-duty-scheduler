import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ManualCoverModalComponent } from './manual-cover-modal.component';

describe('ManualCoverModalComponent', () => {
  let component: ManualCoverModalComponent;
  let fixture: ComponentFixture<ManualCoverModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ManualCoverModalComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ManualCoverModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
