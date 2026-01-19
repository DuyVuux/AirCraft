import type { Employee } from '@/types/employee';
import type { Aircraft } from '@/types/aircraft';
import type { MapEdge } from '@/types/mapEditor';
import type { DistanceMatrixEntry } from '@/types/matrix';

const WALKING_SPEED_MPS = 1.4;

export function toAlgoDateTime(datetime: string): string {
    if (!datetime) return datetime;
    if (datetime.includes('T')) {
        return datetime.endsWith('Z') ? datetime : datetime + 'Z';
    }
    return datetime.replace(' ', 'T') + 'Z';
}

export function transformEmployee(emp: Employee): object {
    return {
        employeeId: emp.employeeId,
        eType: {
            role: emp.eType.role,
            certificates: emp.certifications || []
        },
        currentLocation: null,
        workingTimes: emp.workingTimes.map(t => ({
            start: toAlgoDateTime(t.start),
            end: toAlgoDateTime(t.end)
        })),
        breakDuration: emp.breakDuration || 0,
        fixedBreakTimes: (emp.fixedBreakTimes || []).map(t => ({
            start: toAlgoDateTime(t.start),
            end: toAlgoDateTime(t.end)
        })),
        taskCapabilities: emp.taskCapabilities || [],
        certifications: emp.certifications || []
    };
}

export function transformAircraft(ac: Aircraft): object {
    return {
        aircraftId: ac.aircraftId,
        aType: ac.aType,
        location: ac.location,
        timeWindow: {
            start: toAlgoDateTime(ac.timeWindow.start),
            end: toAlgoDateTime(ac.timeWindow.end)
        },
        requiredTasks: ac.requiredTasks.map(task => ({
            taskCode: task.taskCode,
            requiredCertificates: task.requiredCertificates || []
        }))
    };
}

export function transformEdgesToDistanceMatrix(edges: MapEdge[]): DistanceMatrixEntry[] {
    if (!edges || edges.length === 0) {
        console.warn('[transformForAlgo] No edges provided for distance matrix');
        return [];
    }

    return edges.map(edge => ({
        srcCode: edge.nodeA,
        destCode: edge.nodeB,
        travelTime: edge.travelTime || Math.round(edge.distance / WALKING_SPEED_MPS)
    }));
}
