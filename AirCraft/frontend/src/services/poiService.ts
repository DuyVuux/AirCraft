import type { Location, LocationType } from '@/types/aircraft';

export interface POIFeature {
  type: 'Feature';
  geometry: {
    type: 'Point' | 'Polygon' | 'MultiPolygon';
    coordinates:
    | [number, number] // Point: [longitude, latitude]
    | number[][][] // Polygon: [[[lon, lat], ...]]
    | number[][][][]; // MultiPolygon: [[[[lon, lat], ...]]]
  };
  properties: {
    locationId: string; // OSM @id (e.g., "way/1456456528")
    locationType: LocationType;
    method: string;
  };
  // Store original OSM @id for reference
  osmId?: string;
}

export interface POICollection {
  type: 'FeatureCollection';
  features: POIFeature[];
}

let poiCache: POICollection | null = null;
let hubPoiCache: POICollection | null = null;

/**
 * Load aircraft stands POI from GeoJSON file
 * Uses aircraft_stands_POI.geojson which contains georeferenced coordinates
 * Uses OSM @id as unique identifier for each POI
 */
export async function loadAircraftStandsPOI(): Promise<POICollection> {
  if (poiCache) {
    return poiCache;
  }

  try {
    const response = await fetch('/data/aircraft_stands_POI.geojson', {
      headers: { 'ngrok-skip-browser-warning': 'true' }
    });
    if (!response.ok) {
      throw new Error(`Failed to load POI data: ${response.statusText}`);
    }
    const rawData: any = await response.json();

    // Transform the data: use OSM @id as locationId (unique identifier)
    // Support Point, Polygon, and MultiPolygon geometries
    const transformedFeatures: POIFeature[] = rawData.features
      .map((feature: any) => {
        // Use OSM @id as the unique identifier
        const osmId = feature.properties['@id'] || feature.id || '';
        if (!osmId) {
          return null; // Skip features without OSM ID
        }

        // Preserve original geometry type (Point, Polygon, MultiPolygon)
        const geometryType = feature.geometry.type;

        return {
          type: 'Feature',
          geometry: {
            type: geometryType,
            coordinates: feature.geometry.coordinates,
          } as POIFeature['geometry'],
          properties: {
            locationId: osmId, // Use OSM @id as locationId
            locationType: (feature.properties.locationType as LocationType) || 'APRON',
            method: feature.properties.method || 'georeferenced_extraction',
          },
          osmId: osmId, // Store original OSM ID for reference
        } as POIFeature;
      })
      .filter((feature: POIFeature | null) => feature !== null) as POIFeature[];

    const transformedData: POICollection = {
      type: 'FeatureCollection',
      features: transformedFeatures,
    };

    poiCache = transformedData;
    return transformedData;
  } catch (error) {
    console.error('Error loading aircraft stands POI:', error);
    // Return empty collection on error
    return {
      type: 'FeatureCollection',
      features: [],
    };
  }
}

/**
 * Get POI by locationId (OSM @id) and calculate centroid
 */
export async function getPOIByLocationId(locationId: string): Promise<Location | null> {
  const poiData = await loadAircraftStandsPOI();
  const feature = poiData.features.find(
    (f) => f.properties.locationId === locationId
  );

  if (!feature) {
    return null;
  }

  // Calculate centroid based on geometry type
  let longitude: number, latitude: number;

  if (feature.geometry.type === 'Point') {
    [longitude, latitude] = feature.geometry.coordinates as [number, number];
  } else {
    // For Polygon/MultiPolygon, calculate centroid using turf
    const turf = await import('@turf/turf');
    const geoJsonFeature = feature as any;
    const centroid = turf.centroid(geoJsonFeature);
    [longitude, latitude] = centroid.geometry.coordinates;
  }

  return {
    locationId: feature.properties.locationId, // OSM @id
    locationType: feature.properties.locationType,
    longitude,
    latitude,
  };
}

/**
 * Get all location IDs (OSM @ids) from POI data
 */
export async function getAllLocationIds(): Promise<string[]> {
  const poiData = await loadAircraftStandsPOI();
  return poiData.features.map((f) => f.properties.locationId);
}

/**
 * Load Hub POI from GeoJSON file
 * Uses hubs_POI.geojson if available, otherwise falls back to aircraft stands POI
 * Uses OSM @id as unique identifier for each POI
 */
export async function loadHubPOI(): Promise<POICollection> {
  if (hubPoiCache) {
    return hubPoiCache;
  }

  try {
    // Try to load hubs-specific POI file first
    const response = await fetch('/data/hubs_POI.geojson', {
      headers: { 'ngrok-skip-browser-warning': 'true' }
    });
    if (!response.ok) {
      // If hubs POI file doesn't exist, fall back to aircraft stands POI
      // This allows using the same POI data until hubs-specific file is available
      return await loadAircraftStandsPOI();
    }
    const rawData: any = await response.json();

    // Transform the data: use OSM @id as locationId (unique identifier)
    // Support Point, Polygon, and MultiPolygon geometries
    const transformedFeatures: POIFeature[] = rawData.features
      .map((feature: any) => {
        // Use OSM @id as the unique identifier
        const osmId = feature.properties['@id'] || feature.id || '';
        if (!osmId) {
          return null; // Skip features without OSM ID
        }

        // Preserve original geometry type (Point, Polygon, MultiPolygon)
        const geometryType = feature.geometry.type;

        return {
          type: 'Feature',
          geometry: {
            type: geometryType,
            coordinates: feature.geometry.coordinates,
          } as POIFeature['geometry'],
          properties: {
            locationId: osmId, // Use OSM @id as locationId
            locationType: (feature.properties.locationType as LocationType) || 'HUB',
            method: feature.properties.method || 'georeferenced_extraction',
          },
          osmId: osmId, // Store original OSM ID for reference
        } as POIFeature;
      })
      .filter((feature: POIFeature | null) => feature !== null) as POIFeature[];

    const transformedData: POICollection = {
      type: 'FeatureCollection',
      features: transformedFeatures,
    };

    hubPoiCache = transformedData;
    return transformedData;
  } catch (error) {
    console.error('Error loading Hub POI, falling back to aircraft stands POI:', error);
    // Fall back to aircraft stands POI if hubs POI file doesn't exist
    return await loadAircraftStandsPOI();
  }
}

/**
 * Get Hub POI by locationId (OSM @id) and calculate centroid
 */
export async function getHubPOIByLocationId(locationId: string): Promise<Location | null> {
  const poiData = await loadHubPOI();
  const feature = poiData.features.find(
    (f) => f.properties.locationId === locationId
  );

  if (!feature) {
    return null;
  }

  // Calculate centroid based on geometry type
  let longitude: number, latitude: number;

  if (feature.geometry.type === 'Point') {
    [longitude, latitude] = feature.geometry.coordinates as [number, number];
  } else {
    // For Polygon/MultiPolygon, calculate centroid using turf
    const turf = await import('@turf/turf');
    const geoJsonFeature = feature as any;
    const centroid = turf.centroid(geoJsonFeature);
    [longitude, latitude] = centroid.geometry.coordinates;
  }

  return {
    locationId: feature.properties.locationId, // OSM @id
    locationType: feature.properties.locationType,
    longitude,
    latitude,
  };
}

/**
 * Clear cache (useful for development/testing)
 */
export function clearPOICache(): void {
  poiCache = null;
  hubPoiCache = null;
}

