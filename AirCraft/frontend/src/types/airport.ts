export interface AirportConfig {
    id: string;
    name: string;
    center: {
        lat: number;
        lng: number;
    };
    defaultZoom: number;
    dataFile: string;
}

export interface AirportsConfig {
    airports: AirportConfig[];
    defaultAirportId: string;
}

export interface AirportData {
    mapNodes: import('./mapEditor').MapNode[];
    mapEdges: import('./mapEditor').MapEdge[];
    mapTrips: import('./mapEditor').MapTrip[];
    hubs: import('./hub').Hub[];
    sourceFiles?: {
        aircraftStands?: string;
        hubs?: string;
    };
}

const BACKEND_API = '/api/airports';

export const airportApi = {
    async getConfig(): Promise<AirportsConfig> {
        const response = await fetch(`${BACKEND_API}?t=${Date.now()}`);
        if (!response.ok) throw new Error('Failed to load airports config');
        return response.json();
    },

    async getAirportData(airportId: string): Promise<AirportData> {
        const response = await fetch(`${BACKEND_API}/${airportId}/data?t=${Date.now()}`);
        if (!response.ok) throw new Error(`Failed to load data for ${airportId}`);
        return response.json();
    },

    async saveAirportData(airportId: string, data: AirportData): Promise<void> {
        const response = await fetch(`${BACKEND_API}/${airportId}/data`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to save airport data');
    },

    async createAirport(config: { name: string; center: { lat: number; lng: number }; defaultZoom?: number }): Promise<AirportConfig> {
        const response = await fetch(`${BACKEND_API}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config),
        });
        if (!response.ok) throw new Error('Failed to create airport');
        return response.json();
    },

    async deleteAirport(airportId: string): Promise<void> {
        const response = await fetch(`${BACKEND_API}/${airportId}`, {
            method: 'DELETE',
        });
        if (!response.ok) throw new Error('Failed to delete airport');
    },

    async uploadGeoJSON(file: File, airportName: string, center: { lat: number; lng: number }): Promise<AirportConfig> {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('name', airportName);
        formData.append('centerLat', center.lat.toString());
        formData.append('centerLng', center.lng.toString());

        const response = await fetch(`${BACKEND_API}/upload`, {
            method: 'POST',
            body: formData,
        });
        if (!response.ok) throw new Error('Failed to upload GeoJSON');
        return response.json();
    },
};
