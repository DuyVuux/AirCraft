import { VALIDATION } from './constants';
import { Role, Level } from '@/types/employee';
import { AircraftTypeId } from '@/types/aircraft';

export const validateEmployeeId = (id: string): boolean => {
  return /^EMP_\d+$/.test(id);
};

export const validateAircraftId = (id: string): boolean => {
  return /^[A-Z]{2}-[A-Z0-9]+$/.test(id);
};

export const validateHubId = (id: string): boolean => {
  return /^HUB_\d+$/.test(id);
};

export const validateRole = (role: string): role is Role => {
  const validRoles: Role[] = [
    'MECHANIC',
    'CLEANER',
    'BAGGAGE_HANDLER',
    'REFUEL_TECHNICIAN',
    'GATE_AGENT',
    'PUSHBACK_OPERATOR',
    'CATERING_STAFF',
  ];
  return validRoles.includes(role as Role);
};

export const validateLevel = (level: number): level is Level => {
  return level >= VALIDATION.level.min;
};

export const validateAircraftType = (type: string): type is AircraftTypeId => {
  const validTypes: AircraftTypeId[] = ['A320', 'B737', 'B787', 'A350', 'B777', 'A380'];
  return validTypes.includes(type as AircraftTypeId);
};

export const validateLongitude = (lon: number): boolean => {
  return lon >= VALIDATION.longitude.min && lon <= VALIDATION.longitude.max;
};

export const validateLatitude = (lat: number): boolean => {
  return lat >= VALIDATION.latitude.min && lat <= VALIDATION.latitude.max;
};

export const validateTaskCode = (code: string): boolean => {
  return /^TASK_[A-Z_]+$/.test(code);
};

export const validateLocation = (location: string): boolean => {
  const patterns = [
    /^GATE-\d+$/,
    /^HANGAR-\d+$/,
    /^APRON-\d+$/,
    /^REST_AREA_[A-Z]$/,
    /^MAINTENANCE_HUB$/,
  ];
  return patterns.some(pattern => pattern.test(location));
};

export const validateTimeWindow = (start: string, end: string): boolean => {
  const startDate = new Date(start);
  const endDate = new Date(end);
  return startDate < endDate;
};

export const validateWorkingTime = (start: string, end: string): boolean => {
  const startDate = new Date(start);
  const endDate = new Date(end);
  return startDate < endDate;
};

export const validateBreakTime = (start: string, end: string): boolean => {
  const [startHour, startMin] = start.split(':').map(Number);
  const [endHour, endMin] = end.split(':').map(Number);
  const startMinutes = startHour * 60 + startMin;
  const endMinutes = endHour * 60 + endMin;
  return startMinutes < endMinutes;
};

