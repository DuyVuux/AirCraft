import { useState, useCallback } from 'react';
import type { Hub } from '@/types/hub';
import type { MapNode } from '@/types/mapEditor';
import type { AirportConfig } from '@/types/airport';
import { airportApi } from '@/types/airport';

export interface AirportState {
    mapNodes: MapNode[];
    hubs: Hub[];
    currentAirport: AirportConfig | null;
}

export interface UseAirportDataReturn extends AirportState {
    setMapNodes: React.Dispatch<React.SetStateAction<MapNode[]>>;
    setHubs: React.Dispatch<React.SetStateAction<Hub[]>>;
    setCurrentAirport: React.Dispatch<React.SetStateAction<AirportConfig | null>>;
    loadAirportData: (airport: AirportConfig) => Promise<void>;
    resetAirportData: () => void;
}

export function useAirportData(): UseAirportDataReturn {
    const [mapNodes, setMapNodes] = useState<MapNode[]>([]);
    const [hubs, setHubs] = useState<Hub[]>([]);
    const [currentAirport, setCurrentAirport] = useState<AirportConfig | null>(null);

    const loadAirportData = useCallback(async (airport: AirportConfig) => {
        setCurrentAirport(airport);
        try {
            const data = await airportApi.getAirportData(airport.id);
            setMapNodes(data.mapNodes || []);
            setHubs(data.hubs || []);
        } catch (e) {
            console.error('Failed to load airport data:', e);
        }
    }, []);

    const resetAirportData = useCallback(() => {
        setCurrentAirport(null);
        setMapNodes([]);
        setHubs([]);
    }, []);

    return {
        mapNodes,
        setMapNodes,
        hubs,
        setHubs,
        currentAirport,
        setCurrentAirport,
        loadAirportData,
        resetAirportData,
    };
}
