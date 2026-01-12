import React, { createContext, useContext, useState, useCallback, useEffect, useMemo } from 'react';
import type { Aircraft } from '@/types/aircraft';
import type { Employee } from '@/types/employee';
import type { Hub } from '@/types/hub';
import type { TimeMatrixEntry } from '@/types/matrix';
import type { MapNode, MapEdge, MapTrip } from '@/types/mapEditor';
import type { AirportConfig } from '@/types/airport';
import { airportApi } from '@/types/airport';
import type { Task } from '@/components/editor/TaskEditor';
import { useDatasetManager, useAutoSaveDataset, useAutoSaveAirport } from '@/hooks/useDatasetManager';

interface GlobalDataState {
    tasks: Task[];
    employees: Employee[];
    hubs: Hub[];
    aircrafts: Aircraft[];
    timeMatrix: TimeMatrixEntry[];
    mapNodes: MapNode[];
    mapEdges: MapEdge[];
    mapTrips: MapTrip[];
    currentAirport: AirportConfig | null;

    setTasks: React.Dispatch<React.SetStateAction<Task[]>>;
    setEmployees: React.Dispatch<React.SetStateAction<Employee[]>>;
    setHubs: React.Dispatch<React.SetStateAction<Hub[]>>;
    setAircrafts: React.Dispatch<React.SetStateAction<Aircraft[]>>;
    setTimeMatrix: React.Dispatch<React.SetStateAction<TimeMatrixEntry[]>>;
    setMapNodes: React.Dispatch<React.SetStateAction<MapNode[]>>;
    setMapEdges: React.Dispatch<React.SetStateAction<MapEdge[]>>;
    setMapTrips: React.Dispatch<React.SetStateAction<MapTrip[]>>;
    setCurrentAirport: React.Dispatch<React.SetStateAction<AirportConfig | null>>;

    handleAirportChange: (airport: AirportConfig) => Promise<void>;
    handleExportJSON: () => void;

    datasetManager: ReturnType<typeof useDatasetManager>;
    isLoading: boolean;
    epsilonWalk: number;
    setEpsilonWalk: React.Dispatch<React.SetStateAction<number>>;
}

const GlobalDataContext = createContext<GlobalDataState | null>(null);

export function useGlobalData() {
    const context = useContext(GlobalDataContext);
    if (!context) {
        throw new Error('useGlobalData must be used within GlobalDataProvider');
    }
    return context;
}

export function GlobalDataProvider({ children }: { children: React.ReactNode }) {
    const [aircrafts, setAircrafts] = useState<Aircraft[]>([]);
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [hubs, setHubs] = useState<Hub[]>([]);
    const [tasks, setTasks] = useState<Task[]>([]);
    const [timeMatrix, setTimeMatrix] = useState<TimeMatrixEntry[]>([]);
    const [mapNodes, setMapNodes] = useState<MapNode[]>([]);
    const [mapEdges, setMapEdges] = useState<MapEdge[]>([]);
    const [mapTrips, setMapTrips] = useState<MapTrip[]>([]);
    const [currentAirport, setCurrentAirport] = useState<AirportConfig | null>(null);
    const [epsilonWalk, setEpsilonWalk] = useState<number>(50.0);

    const onDataLoaded = useCallback((data: Partial<{
        tasks: Task[]; employees: Employee[]; hubs: Hub[];
        aircrafts: Aircraft[]; timeMatrix: TimeMatrixEntry[];
    }>) => {
        if (data.tasks !== undefined) setTasks(data.tasks);
        if (data.employees !== undefined) setEmployees(data.employees);
        if (data.hubs !== undefined) setHubs(data.hubs);
        if (data.aircrafts !== undefined) setAircrafts(data.aircrafts);
        if (data.timeMatrix !== undefined) setTimeMatrix(data.timeMatrix);
    }, []);

    const onResetEditingState = useCallback(() => { }, []);

    const datasetManager = useDatasetManager({ onDataLoaded, onResetEditingState });

    useAutoSaveDataset({
        isLoaded: datasetManager.isLoaded,
        currentDatasetId: datasetManager.currentDatasetId,
        isSwapping: datasetManager.isSwapping,
        data: { tasks, employees, aircrafts, timeMatrix },
        setDatasets: datasetManager.setDatasets,
    });

    useAutoSaveAirport({
        isLoaded: datasetManager.isLoaded,
        currentAirport,
        mapNodes,
        mapEdges,
        mapTrips,
        hubs,
    });

    useEffect(() => { datasetManager.initializeDatasets(); }, [datasetManager.initializeDatasets]);

    const handleAirportChange = useCallback(async (airport: AirportConfig) => {
        setCurrentAirport(airport);
        // Clear trip cache to force regeneration with new backend logic
        localStorage.removeItem(`trip_cache_hash_${airport.id}`);
        localStorage.removeItem(`trip_cache_trips_${airport.id}`);
        try {
            const data = await airportApi.getAirportData(airport.id);
            setMapNodes(data.mapNodes || []);
            setMapEdges(data.mapEdges || []);
            // DON'T load mapTrips from saved data - let backend regenerate
            setMapTrips([]);
            setHubs(data.hubs || []);
        } catch (e) {
            console.error('Failed to load airport data:', e);
        }
    }, []);

    // Auto-generate trips using Floyd-Warshall when map changes
    useEffect(() => {
        if (!currentAirport || mapNodes.length === 0 || mapEdges.length === 0) return;

        const cachedHash = localStorage.getItem(`trip_cache_hash_${currentAirport.id}`);
        const cachedTrips = localStorage.getItem(`trip_cache_trips_${currentAirport.id}`);

        // Call backend API to generate trips
        fetch('/api/map/generate-trips', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                airportId: currentAirport.id,
                nodes: mapNodes,
                edges: mapEdges,
                cachedHash,
                epsilon_walk: epsilonWalk
            })
        })
            .then(res => {
                if (!res.ok) {
                    throw new Error(`API returned ${res.status}`);
                }
                return res.json();
            })
            .then(data => {
                if (data.cached && cachedTrips) {
                    // Use cached trips
                    setMapTrips(JSON.parse(cachedTrips));
                    console.log('Using cached trips');
                } else if (data.trips && Array.isArray(data.trips)) {
                    // Use newly generated trips
                    setMapTrips(data.trips);
                    if (data.cacheKey) {
                        localStorage.setItem(`trip_cache_hash_${currentAirport.id}`, data.cacheKey);
                        localStorage.setItem(`trip_cache_trips_${currentAirport.id}`, JSON.stringify(data.trips));
                    }
                    console.log(`Generated ${data.trips.length} trips using Floyd-Warshall`);
                } else {
                    console.warn('No trips data returned from API');
                }
            })
            .catch(err => {
                console.error('Failed to generate trips:', err);
                // Use cached trips if available when API fails
                if (cachedTrips) {
                    try {
                        setMapTrips(JSON.parse(cachedTrips));
                        console.log('Using cached trips after API failure');
                    } catch {
                        console.error('Failed to parse cached trips');
                    }
                }
            });
    }, [currentAirport, mapNodes, mapEdges, epsilonWalk]);

    const handleExportJSON = useCallback(() => {
        const trackingId = `PLAN-${new Date().toISOString().split('T')[0]}-${String(Math.floor(Math.random() * 1000)).padStart(3, '0')}`;

        const data = {
            trackingId,
            aircrafts,
            hubs,
            employees,
            matrixConfigs: {
                distanceMatrix: [],
                busTransitMatrix: [],
                walkingDistanceFromLocationToBusStop: [],
                timeMatrix
            }
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `input_data_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }, [aircrafts, employees, hubs, timeMatrix]);

    const value = useMemo(() => ({
        tasks, employees, hubs, aircrafts, timeMatrix, mapNodes, mapEdges, mapTrips, currentAirport,
        setTasks, setEmployees, setHubs, setAircrafts, setTimeMatrix, setMapNodes, setMapEdges, setMapTrips, setCurrentAirport,
        handleAirportChange, handleExportJSON,
        datasetManager,
        isLoading: datasetManager.isLoading,
        epsilonWalk,
        setEpsilonWalk,
    }), [
        tasks, employees, hubs, aircrafts, timeMatrix, mapNodes, mapEdges, mapTrips, currentAirport,
        handleAirportChange, handleExportJSON, datasetManager, epsilonWalk,
    ]);

    return (
        <GlobalDataContext.Provider value={value}>
            {children}
        </GlobalDataContext.Provider>
    );
}
