import type { Aircraft } from '@/types/aircraft';
import type { Employee } from '@/types/employee';
import type { Hub } from '@/types/hub';
import type { Task } from '@/components/editor/TaskEditor';
import type { TimeMatrixEntry } from '@/types/matrix';
import type { MapNode } from '@/types/mapEditor';
import type { AirportConfig } from '@/types/airport';

export interface TabConfig {
    id: string;
    label: string;
    order: number;
}

export interface TabProps {
    // Data arrays
    tasks: Task[];
    employees: Employee[];
    hubs: Hub[];
    aircrafts: Aircraft[];
    timeMatrix: TimeMatrixEntry[];
    mapNodes: MapNode[];
    currentAirport: AirportConfig | null;

    // Setters
    setTasks: (v: Task[]) => void;
    setEmployees: (v: Employee[]) => void;
    setHubs: (v: Hub[]) => void;
    setAircrafts: (v: Aircraft[]) => void;
    setTimeMatrix: (v: TimeMatrixEntry[]) => void;
    setMapNodes: (v: MapNode[]) => void;

    // Edit states
    editingTask: Task | null;
    setEditingTask: (task: Task | null) => void;
    editingEmployeeId: string | null;
    setEditingEmployeeId: (id: string | null) => void;
    editingHubId: string | null;
    setEditingHubId: (id: string | null) => void;
    editingAircraftId: string | null;
    setEditingAircraftId: (id: string | null) => void;
    editingTimeMatrixIndex: number | null;
    setEditingTimeMatrixIndex: (index: number | null) => void;

    // Handlers
    handleTaskSave: (task: Task) => void;
    handleTaskDelete: (taskCode: string) => void;
    handleTaskEdit: (task: Task) => void;

    handleEmployeeSave: (employee: Employee) => void;
    handleEmployeeDelete: (employeeId: string) => void;

    handleHubSave: (hub: Hub) => void;
    handleHubDelete: (hubId: string) => void;

    handleAircraftSave: (aircraft: Aircraft) => void;
    handleAircraftDelete: (aircraftId: string) => void;
    handleAircraftBulkDelete: (aircraftIds: string[]) => void;

    handleTimeMatrixSave: (entry: TimeMatrixEntry, originalIndex?: number) => void;
    handleTimeMatrixDelete: (index: number) => void;

    // Computed values
    availableTaskCodes: string[];
    availableAircraftIds: string[];
    taskMap: Map<string, Task>;
}
