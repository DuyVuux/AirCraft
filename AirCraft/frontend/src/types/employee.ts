export type Role =
  | 'MECHANIC'
  | 'CLEANER'
  | 'BAGGAGE_HANDLER'
  | 'REFUEL_TECHNICIAN'
  | 'GATE_AGENT'
  | 'PUSHBACK_OPERATOR'
  | 'CATERING_STAFF';

export interface EmployeeType {
  role: Role;
  certificates?: string[];
}

export interface WorkingTime {
  start: string; // ISO 8601 format with 'Z'
  end: string; // ISO 8601 format with 'Z'
}

export interface BreakTime {
  start: string; // HH:MM format (old format)
  end: string; // HH:MM format (old format)
}

export interface FixedBreakTime {
  start: string; // ISO 8601 format with 'Z'
  end: string; // ISO 8601 format with 'Z'
}

export interface Employee {
  employeeId: string;
  name?: string; // Tên NV
  position?: string; // Chức Danh (Nhân viên, Kỹ sư, Đội trưởng, etc.)
  eType: EmployeeType;
  taskCapabilities?: string[]; // Năng Lực (Tasks): ['ARR-A', 'DEP-A', 'TOW', 'WO-01']
  certifications?: string[]; // Chứng Chỉ (Certs): ['A321', 'B787', 'A330']
  workingTimes: WorkingTime[];
  breakTimes?: BreakTime[]; // Old format (HH:MM)
  breakDuration?: number; // New format: break duration in seconds
  fixedBreakTimes?: FixedBreakTime[]; // New format: fixed break times (ISO format)
}

export const ROLES: Role[] = [
  'MECHANIC',
  'CLEANER',
  'BAGGAGE_HANDLER',
  'REFUEL_TECHNICIAN',
  'GATE_AGENT',
  'PUSHBACK_OPERATOR',
  'CATERING_STAFF',
];



