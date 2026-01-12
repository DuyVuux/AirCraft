/**
 * Calculate distance between two GPS coordinates using Haversine formula
 * @param lat1 Latitude of first point
 * @param lon1 Longitude of first point
 * @param lat2 Latitude of second point
 * @param lon2 Longitude of second point
 * @returns Distance in kilometers
 */
export const calculateDistance = (
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number => {
  const R = 6371; // Earth's radius in kilometers
  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(lat1)) *
      Math.cos(toRadians(lat2)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c;

  return Math.round(distance * 100) / 100; // Round to 2 decimal places
};

const toRadians = (degrees: number): number => {
  return degrees * (Math.PI / 180);
};

/**
 * Generate distance matrix for all location pairs
 */
export interface Location {
  location: string;
  longitude: number;
  latitude: number;
}

export const generateDistanceMatrix = (
  locations: Location[]
): Array<{ source: string; destination: string; value: number }> => {
  const matrix: Array<{ source: string; destination: string; value: number }> = [];

  for (const source of locations) {
    for (const destination of locations) {
      if (source.location === destination.location) {
        matrix.push({
          source: source.location,
          destination: destination.location,
          value: 0,
        });
      } else {
        const distance = calculateDistance(
          source.latitude,
          source.longitude,
          destination.latitude,
          destination.longitude
        );
        matrix.push({
          source: source.location,
          destination: destination.location,
          value: distance,
        });
      }
    }
  }

  return matrix;
};

