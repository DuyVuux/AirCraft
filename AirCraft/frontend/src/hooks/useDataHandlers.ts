import { useCallback } from 'react';
import type { Aircraft } from '@/types/aircraft';
import type { Employee } from '@/types/employee';
import type { Hub } from '@/types/hub';
import type { Task } from '@/components/editor/TaskEditor';
import type { TimeMatrixEntry } from '@/types/matrix';

interface DataState {
    aircrafts: Aircraft[];
    setAircrafts: React.Dispatch<React.SetStateAction<Aircraft[]>>;
    employees: Employee[];
    setEmployees: React.Dispatch<React.SetStateAction<Employee[]>>;
    hubs: Hub[];
    setHubs: React.Dispatch<React.SetStateAction<Hub[]>>;
    tasks: Task[];
    setTasks: React.Dispatch<React.SetStateAction<Task[]>>;
    timeMatrix: TimeMatrixEntry[];
    setTimeMatrix: React.Dispatch<React.SetStateAction<TimeMatrixEntry[]>>;
    editingTask: Task | null;
    setEditingTask: React.Dispatch<React.SetStateAction<Task | null>>;
    setEditingAircraftId: React.Dispatch<React.SetStateAction<string | null>>;
    setEditingEmployeeId: React.Dispatch<React.SetStateAction<string | null>>;
    setEditingHubId: React.Dispatch<React.SetStateAction<string | null>>;
    setEditingTimeMatrixIndex: React.Dispatch<React.SetStateAction<number | null>>;
}

export function useDataHandlers(state: DataState) {
    const {
        aircrafts, setAircrafts,
        employees, setEmployees,
        hubs, setHubs,
        tasks, setTasks,
        timeMatrix, setTimeMatrix,
        editingTask, setEditingTask,
        setEditingAircraftId, setEditingEmployeeId, setEditingHubId, setEditingTimeMatrixIndex
    } = state;

    const handleAircraftSave = useCallback((aircraft: Aircraft) => {
        const index = aircrafts.findIndex((a) => a.aircraftId === aircraft.aircraftId);
        if (index >= 0) {
            setAircrafts((prev) => {
                const newList = [...prev];
                newList[index] = aircraft;
                return newList;
            });
            setEditingAircraftId(null);
        } else {
            setAircrafts((prev) => [...prev, aircraft]);
        }
    }, [aircrafts, setAircrafts, setEditingAircraftId]);

    const handleAircraftDelete = useCallback((aircraftId: string) => {
        setAircrafts((prev) => prev.filter((a) => a.aircraftId !== aircraftId));
    }, [setAircrafts]);

    const handleAircraftBulkDelete = useCallback((aircraftIds: string[]) => {
        const idsToDelete = new Set(aircraftIds);
        setAircrafts((prev) => prev.filter((a) => !idsToDelete.has(a.aircraftId)));
    }, [setAircrafts]);

    const handleEmployeeSave = useCallback((employee: Employee) => {
        const index = employees.findIndex((e) => e.employeeId === employee.employeeId);
        if (index >= 0) {
            setEmployees((prev) => {
                const newList = [...prev];
                newList[index] = employee;
                return newList;
            });
            setEditingEmployeeId(null);
        } else {
            setEmployees((prev) => [...prev, employee]);
        }
    }, [employees, setEmployees, setEditingEmployeeId]);

    const handleEmployeeDelete = useCallback((employeeId: string) => {
        setEmployees((prev) => prev.filter((e) => e.employeeId !== employeeId));
    }, [setEmployees]);

    const handleHubSave = useCallback((hub: Hub) => {
        const index = hubs.findIndex((h) => h.hubId === hub.hubId);
        if (index >= 0) {
            setHubs((prev) => {
                const newList = [...prev];
                newList[index] = hub;
                return newList;
            });
            setEditingHubId(null);
        } else {
            setHubs((prev) => [...prev, hub]);
        }
    }, [hubs, setHubs, setEditingHubId]);

    const handleHubDelete = useCallback((hubId: string) => {
        setHubs((prev) => prev.filter((h) => h.hubId !== hubId));
    }, [setHubs]);

    const handleTimeMatrixSave = useCallback((entry: TimeMatrixEntry, originalIndex?: number) => {
        if (originalIndex !== undefined && originalIndex >= 0 && originalIndex < timeMatrix.length) {
            setTimeMatrix((prev) => {
                const newList = [...prev];
                newList[originalIndex] = entry;
                return newList;
            });
            setEditingTimeMatrixIndex(null);
        } else {
            const existingIndex = timeMatrix.findIndex(
                (e) =>
                    e.taskCode === entry.taskCode &&
                    (e.role || '') === (entry.role || '') &&
                    (e.level || 0) === (entry.level || 0) &&
                    (e.aircraftId || '') === (entry.aircraftId || '')
            );
            if (existingIndex >= 0) {
                setTimeMatrix((prev) => {
                    const newList = [...prev];
                    newList[existingIndex] = entry;
                    return newList;
                });
            } else {
                setTimeMatrix((prev) => [...prev, entry]);
            }
        }
    }, [timeMatrix, setTimeMatrix, setEditingTimeMatrixIndex]);

    const handleTimeMatrixDelete = useCallback((index: number) => {
        setTimeMatrix((prev) => prev.filter((_, i) => i !== index));
    }, [setTimeMatrix]);

    const handleTaskSave = useCallback((task: Task) => {
        const index = tasks.findIndex((t) => t.taskCode === task.taskCode);
        if (index >= 0) {
            setTasks((prev) => {
                const newList = [...prev];
                newList[index] = task;
                return newList;
            });
        } else {
            setTasks((prev) => [...prev, task]);
        }
        setEditingTask(null);
    }, [tasks, setTasks, setEditingTask]);

    const handleTaskDelete = useCallback((taskCode: string) => {
        setTasks((prev) => prev.filter((t) => t.taskCode !== taskCode));
        if (editingTask?.taskCode === taskCode) {
            setEditingTask(null);
        }
    }, [setTasks, editingTask, setEditingTask]);

    const handleTaskEdit = useCallback((task: Task) => {
        setEditingTask(task);
    }, [setEditingTask]);

    return {
        handleAircraftSave,
        handleAircraftDelete,
        handleAircraftBulkDelete,
        handleEmployeeSave,
        handleEmployeeDelete,
        handleHubSave,
        handleHubDelete,
        handleTimeMatrixSave,
        handleTimeMatrixDelete,
        handleTaskSave,
        handleTaskDelete,
        handleTaskEdit,
    };
}
