import { describe, test, expect } from 'vitest';
import {
    toAlgoDateTime,
    transformEmployee,
    transformAircraft,
    transformEdgesToDistanceMatrix
} from './transformForAlgo';
import type { Employee } from '@/types/employee';
import type { Aircraft } from '@/types/aircraft';
import type { MapEdge } from '@/types/mapEditor';

describe('toAlgoDateTime', () => {
    test('converts space separator to T and adds Z', () => {
        expect(toAlgoDateTime('2022-01-31 00:00:00')).toBe('2022-01-31T00:00:00Z');
    });

    test('keeps ISO format with Z unchanged', () => {
        expect(toAlgoDateTime('2024-12-05T08:00:00Z')).toBe('2024-12-05T08:00:00Z');
    });

    test('adds Z to ISO without timezone', () => {
        expect(toAlgoDateTime('2024-12-05T08:00:00')).toBe('2024-12-05T08:00:00Z');
    });

    test('handles empty string', () => {
        expect(toAlgoDateTime('')).toBe('');
    });

    test('handles null/undefined', () => {
        expect(toAlgoDateTime(null as any)).toBe(null);
        expect(toAlgoDateTime(undefined as any)).toBe(undefined);
    });
});

describe('transformEmployee', () => {
    test('maps taskCapabilities to eType.certificates', () => {
        const emp: Partial<Employee> = {
            employeeId: 'E001',
            eType: { role: 'MECHANIC' },
            taskCapabilities: ['DEP-A', 'ARR-A'],
            workingTimes: [{ start: '2022-01-01 08:00:00', end: '2022-01-01 16:00:00' }],
            breakDuration: 0,
            fixedBreakTimes: []
        };

        const result = transformEmployee(emp as Employee) as any;

        expect(result.eType.certificates).toEqual(['DEP-A', 'ARR-A']);
        expect(result.currentLocation).toBeNull();
        expect(result.workingTimes[0].start).toBe('2022-01-01T08:00:00Z');
    });

    test('handles empty taskCapabilities', () => {
        const emp: Partial<Employee> = {
            employeeId: 'E002',
            eType: { role: 'MECHANIC' },
            workingTimes: [],
            breakDuration: 0,
            fixedBreakTimes: []
        };

        const result = transformEmployee(emp as Employee) as any;

        expect(result.eType.certificates).toEqual([]);
    });
});

describe('transformAircraft', () => {
    test('adds requiredCertificates based on taskCode', () => {
        const ac: Partial<Aircraft> = {
            aircraftId: 'VN19-1',
            aType: { id: 'A350', desc: 'Airbus A350' },
            location: { locationId: 'loc1', locationType: 'APRON', longitude: 0, latitude: 0 },
            timeWindow: { start: '2022-01-31 00:00:00', end: '2022-01-31 18:00:00' },
            requiredTasks: [
                { taskCode: 'DEP-M' },
                { taskCode: 'DEP-A' }
            ]
        };

        const result = transformAircraft(ac as Aircraft) as any;

        expect(result.requiredTasks[0].requiredCertificates).toEqual(['DEP-M']);
        expect(result.requiredTasks[1].requiredCertificates).toEqual(['DEP-A']);
        expect(result.timeWindow.start).toBe('2022-01-31T00:00:00Z');
    });
});

describe('transformEdgesToDistanceMatrix', () => {
    test('converts edge to distance entry with travelTime', () => {
        const edges: Partial<MapEdge>[] = [{
            id: 'e1',
            nodeA: 'node-A',
            nodeB: 'node-B',
            distance: 140,
            travelTime: 100,
            directed: false
        }];

        const result = transformEdgesToDistanceMatrix(edges as MapEdge[]);

        expect(result[0].srcCode).toBe('node-A');
        expect(result[0].destCode).toBe('node-B');
        expect(result[0].travelTime).toBe(100);
    });

    test('calculates travelTime from distance if not provided', () => {
        const edges: Partial<MapEdge>[] = [{
            id: 'e2',
            nodeA: 'A',
            nodeB: 'B',
            distance: 140,
            directed: false
        }];

        const result = transformEdgesToDistanceMatrix(edges as MapEdge[]);

        expect(result[0].travelTime).toBe(100);
    });

    test('handles empty edges array', () => {
        const result = transformEdgesToDistanceMatrix([]);
        expect(result).toEqual([]);
    });
});
