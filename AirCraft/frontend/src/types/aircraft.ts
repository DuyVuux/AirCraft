export interface AircraftType {
  id: string;
  desc: string;
}

export interface TimeWindow {
  start: string; // ISO 8601 format with 'Z'
  end: string; // ISO 8601 format with 'Z'
}

export type LocationType = 'GATE' | 'HANGAR' | 'APRON' | 'HUB' | 'REST_AREA';

export interface Location {
  id?: string;
  locationId: string;
  locationType: LocationType;
  longitude: number;
  latitude: number;
}

export interface RequiredTask {
  taskCode: string;
  minLevel?: number;
}

export interface Aircraft {
  aircraftId: string; // Mã máy bay (unique ID)
  registrationNumber?: string; // Số hiệu đăng ký (VN-A123)
  flightNumber?: string; // Mã chuyến bay (VN123)
  aType: AircraftType;
  location: Location; // Always object format with locationId, locationType, longitude, latitude
  timeWindow: TimeWindow;
  requiredTasks: RequiredTask[];
}

export type AircraftTypeId = 'A320' | 'B737' | 'B787' | 'A350' | 'B777' | 'A380';

export const AIRCRAFT_TYPES: Record<AircraftTypeId, string> = {
  A320: 'Airbus A320',
  B737: 'Boeing 737',
  B787: 'Boeing 787',
  A350: 'Airbus A350',
  B777: 'Boeing 777',
  A380: 'Airbus A380',
};

