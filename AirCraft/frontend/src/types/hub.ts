import { Location } from './aircraft';

export interface Hub {
  hubId: string;
  name?: string; // Tên hub (optional)
  location: Location; // Always object format with locationId, locationType, longitude, latitude
}

