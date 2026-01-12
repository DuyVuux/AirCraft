import { useState, useCallback, useRef, useEffect } from 'react';
import type { Aircraft } from '@/types/aircraft';
import type { Employee } from '@/types/employee';
import type { Hub } from '@/types/hub';
import type { Task } from '@/components/editor/TaskEditor';
import type { TimeMatrixEntry } from '@/types/matrix';
import type { MapNode, MapEdge, MapTrip } from '@/types/mapEditor';
import type { DatasetMeta, DatasetData } from '@/types/dataset';
import type { AirportConfig } from '@/types/airport';
import { api } from '@/types/dataset';
import { airportApi, type AirportData } from '@/types/airport';

interface DatasetState {
    tasks: Task[];
    employees: Employee[];
    aircrafts: Aircraft[];
    timeMatrix: TimeMatrixEntry[];
}

interface UseDatasetManagerOptions {
    onDataLoaded: (data: Partial<DatasetState>) => void;
    onResetEditingState: () => void;
}

export function useDatasetManager(options: UseDatasetManagerOptions) {
    const { onDataLoaded, onResetEditingState } = options;

    const [datasets, setDatasets] = useState<DatasetMeta[]>([]);
    const [currentDatasetId, setCurrentDatasetId] = useState<string | null>(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const isSwapping = useRef(false);
    const initialized = useRef(false);

    const loadDatasetById = useCallback(async (id: string) => {
        setIsLoading(true);
        try {
            const data = await api.getDataset(id);
            if (data) {
                onDataLoaded({
                    tasks: data.tasks || [],
                    employees: data.employees || [],
                    aircrafts: data.aircrafts || [],
                    timeMatrix: data.timeMatrix || [],
                });
            } else {
                onDataLoaded({
                    tasks: [],
                    employees: [],
                    aircrafts: [],
                    timeMatrix: [],
                });
            }
            onResetEditingState();
        } catch (e) {
            console.error('Failed to load dataset:', e);
        } finally {
            setIsLoading(false);
        }
    }, [onDataLoaded, onResetEditingState]);

    const initializeDatasets = useCallback(async () => {
        if (initialized.current) return;
        initialized.current = true;

        let allDatasets = await api.listDatasets();
        if (!allDatasets) {
            console.warn('Failed to list datasets (backend might be down)');
            return;
        }

        if (allDatasets.length === 0) {
            try {
                const { meta } = await api.createDataset('Bộ dữ liệu mặc định');
                allDatasets = [meta];
            } catch (e) {
                console.error('Failed to create default dataset:', e);
                return;
            }
        }

        setDatasets(allDatasets);
        const firstId = allDatasets[0].id;
        setCurrentDatasetId(firstId);
        await loadDatasetById(firstId);
        setIsLoaded(true);
    }, [loadDatasetById]);

    const handleCreateDataset = useCallback(async (name: string) => {
        try {
            const { meta } = await api.createDataset(name);
            setDatasets(prev => [...prev, meta]);
            isSwapping.current = true;
            setCurrentDatasetId(meta.id);
            await loadDatasetById(meta.id);
            setTimeout(() => { isSwapping.current = false; }, 100);
        } catch (e) {
            console.error('Failed to create dataset:', e);
        }
    }, [loadDatasetById]);

    const handleSelectDataset = useCallback((id: string) => {
        if (id !== currentDatasetId) {
            isSwapping.current = true;
            setCurrentDatasetId(id);
            loadDatasetById(id);
            setTimeout(() => { isSwapping.current = false; }, 100);
        }
    }, [currentDatasetId, loadDatasetById]);

    const handleDeleteDataset = useCallback(async (id: string) => {
        if (datasets.length <= 1) return;
        try {
            await api.deleteDataset(id);
            const newDatasets = datasets.filter(ds => ds.id !== id);
            setDatasets(newDatasets);
            if (currentDatasetId === id) {
                isSwapping.current = true;
                const firstId = newDatasets[0].id;
                setCurrentDatasetId(firstId);
                await loadDatasetById(firstId);
                setTimeout(() => { isSwapping.current = false; }, 100);
            }
        } catch (e) {
            console.error('Failed to delete dataset:', e);
        }
    }, [datasets, currentDatasetId, loadDatasetById]);

    const handleRenameDataset = useCallback(async (id: string, name: string) => {
        try {
            await api.renameDataset(id, name);
            setDatasets(prev => prev.map(ds => ds.id === id ? { ...ds, name } : ds));
        } catch (e) {
            console.error('Failed to rename dataset:', e);
        }
    }, []);

    return {
        datasets,
        currentDatasetId,
        isLoaded,
        isLoading,
        isSwapping,
        setDatasets,
        initializeDatasets,
        handleCreateDataset,
        handleSelectDataset,
        handleDeleteDataset,
        handleRenameDataset,
    };
}

interface UseAutoSaveDatasetOptions {
    isLoaded: boolean;
    currentDatasetId: string | null;
    isSwapping: React.MutableRefObject<boolean>;
    data: DatasetState;
    setDatasets: React.Dispatch<React.SetStateAction<DatasetMeta[]>>;
}

export function useAutoSaveDataset(options: UseAutoSaveDatasetOptions) {
    const { isLoaded, currentDatasetId, isSwapping, data, setDatasets } = options;
    const { tasks, employees, aircrafts, timeMatrix } = data;

    useEffect(() => {
        if (!isLoaded || !currentDatasetId || isSwapping.current) return;
        const save = async () => {
            const saveData: DatasetData = { tasks, employees, aircrafts, timeMatrix };
            await api.saveDataset(currentDatasetId, saveData);
            setDatasets(prev => prev.map(ds =>
                ds.id === currentDatasetId
                    ? {
                        ...ds,
                        updatedAt: new Date().toISOString(),
                        itemCounts: {
                            tasks: tasks.length,
                            employees: employees.length,
                            aircrafts: aircrafts.length,
                            timeMatrix: timeMatrix.length,
                        },
                    }
                    : ds
            ));
        };
        save();
    }, [tasks, employees, aircrafts, timeMatrix, isLoaded, currentDatasetId, isSwapping, setDatasets]);
}

interface UseAutoSaveAirportOptions {
    isLoaded: boolean;
    currentAirport: AirportConfig | null;
    mapNodes: MapNode[];
    mapEdges: MapEdge[];
    mapTrips: MapTrip[];
    hubs: Hub[];
}

export function useAutoSaveAirport(options: UseAutoSaveAirportOptions) {
    const { isLoaded, currentAirport, mapNodes, mapEdges, mapTrips, hubs } = options;

    useEffect(() => {
        if (!currentAirport || !isLoaded) return;
        const saveAirport = async () => {
            try {
                const airportData: AirportData = { mapNodes, mapEdges, mapTrips, hubs };
                await airportApi.saveAirportData(currentAirport.id, airportData);
            } catch (e) {
                console.error('Failed to auto-save airport data:', e);
            }
        };
        const timer = setTimeout(saveAirport, 1000);
        return () => clearTimeout(timer);
    }, [mapNodes, mapEdges, mapTrips, hubs, currentAirport, isLoaded]);
}
